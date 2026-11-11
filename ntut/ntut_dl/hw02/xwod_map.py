"""XWOD object-detection metric (COCO-style mAP) for Kaggle.

Kaggle's built-in metrics need a fixed number of values per row. Detection
output does not have that, so each test image is one row and all of its boxes
are packed into a single space-separated ``PredictionString``:

    submission.csv
        image_id,PredictionString
        dust_test_00001,1 0.91 0.5078 0.8025 0.1333 0.1530 0 0.40 0.0478 0.7891 0.0267 0.2082
        wildfire_test_00117,none

    Each box is 6 tokens: ``class conf cx cy w h``, with box coordinates
    normalized to [0, 1] (YOLO format, same as the dataset labels).
    Use the word ``none`` for an image with no detections. Kaggle rejects
    empty cells ("Submission contains null values"); an empty value is still
    accepted by this code for local use.

    solution.csv (host only)
        image_id,PredictionString,weather,Usage
        dust_test_00001,1 0.5078 0.8025 0.1333 0.1530 ...,dust,Public

    Ground-truth boxes are 5 tokens: ``class cx cy w h``.

The score is mAP50-95: AP averaged over IoU thresholds 0.50:0.05:0.95 and over
the classes present in the ground truth. The matching and AP code is a numpy
port of Ultralytics 8.4 (``DetectionValidator.match_predictions``,
``metrics.ap_per_class``, ``metrics.compute_ap``), so leaderboard numbers are
comparable to ``model.val()`` results reported in the XWOD paper. As in
Ultralytics, AP integrates 101 interpolated points with the trapezoid rule, so
a perfect submission scores 0.995 (not 1.0).

Normalized coordinates give the same IoU as pixel coordinates (IoU does not
change when x and y are scaled independently), so image sizes are not needed.

Only numpy and pandas are used.
"""

import numpy as np
import pandas as pd

CLASS_NAMES = ["person", "car", "truck", "motorcycle", "bus", "bike"]
NUM_CLASSES = len(CLASS_NAMES)
PRED_COL = "PredictionString"
WEATHER_COL = "weather"
USAGE_COL = "Usage"
NO_BOX = "none"                      # write this for an image with no detections
NO_BOX_TOKENS = {"", NO_BOX}


class ParticipantVisibleError(Exception):
    pass


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _is_empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and np.isnan(value):
        return True
    return str(value).strip().lower() in NO_BOX_TOKENS


def _parse_boxes(value, n_fields: int, image_id, error_cls, what: str) -> np.ndarray:
    """Parse one PredictionString into an (N, n_fields) float64 array."""
    if _is_empty(value):
        return np.zeros((0, n_fields), dtype=np.float64)
    tokens = str(value).split()
    if len(tokens) % n_fields != 0:
        raise error_cls(
            f"{what} for image_id '{image_id}' has {len(tokens)} values, which is not a "
            f"multiple of {n_fields}. Expected repeated groups of "
            + ("'class conf cx cy w h'." if n_fields == 6 else "'class cx cy w h'.")
        )
    try:
        arr = np.asarray(tokens, dtype=np.float64).reshape(-1, n_fields)
    except ValueError:
        raise error_cls(f"{what} for image_id '{image_id}' contains a value that is not a number.")
    if not np.isfinite(arr).all():
        raise error_cls(f"{what} for image_id '{image_id}' contains NaN or infinite values.")
    cls = arr[:, 0]
    if (cls != np.round(cls)).any() or (cls < 0).any() or (cls >= NUM_CLASSES).any():
        raise error_cls(
            f"{what} for image_id '{image_id}' has a class id outside 0..{NUM_CLASSES - 1}."
        )
    wh = arr[:, -2:]
    if (wh < 0).any():
        raise error_cls(f"{what} for image_id '{image_id}' has a box with negative width or height.")
    return arr


def _cxcywh_to_xyxy(b: np.ndarray) -> np.ndarray:
    out = np.empty_like(b)
    out[:, 0] = b[:, 0] - b[:, 2] / 2
    out[:, 1] = b[:, 1] - b[:, 3] / 2
    out[:, 2] = b[:, 0] + b[:, 2] / 2
    out[:, 3] = b[:, 1] + b[:, 3] / 2
    return out


# ---------------------------------------------------------------------------
# Ultralytics-equivalent core (numpy)
# ---------------------------------------------------------------------------

# Ultralytics adds eps=1e-7 to the union in *pixel* units. Boxes here are normalized
# (areas are ~1e-4 for small objects), so a much smaller eps keeps IoU equivalent.
IOU_EPS = 1e-12


def _box_iou_xyxy(box1: np.ndarray, box2: np.ndarray, eps: float = IOU_EPS) -> np.ndarray:
    """IoU matrix (len(box1), len(box2)); same formula as ultralytics box_iou."""
    a1, a2 = box1[:, None, :2], box1[:, None, 2:]
    b1, b2 = box2[None, :, :2], box2[None, :, 2:]
    inter = np.clip(np.minimum(a2, b2) - np.maximum(a1, b1), 0, None).prod(2)
    area1 = (box1[:, 2:] - box1[:, :2]).prod(1)[:, None]
    area2 = (box2[:, 2:] - box2[:, :2]).prod(1)[None, :]
    return inter / (area1 + area2 - inter + eps)


def _match_predictions(pred_classes, true_classes, iou, iouv) -> np.ndarray:
    """Greedy matching, identical to DetectionValidator.match_predictions (non-scipy).

    iou has shape (n_labels, n_preds). Returns bool array (n_preds, len(iouv)).
    """
    correct = np.zeros((pred_classes.shape[0], len(iouv)), dtype=bool)
    iou = iou * (true_classes[:, None] == pred_classes[None, :])
    for i, threshold in enumerate(iouv):
        matches = np.array(np.nonzero(iou >= threshold)).T
        if matches.shape[0]:
            if matches.shape[0] > 1:
                matches = matches[iou[matches[:, 0], matches[:, 1]].argsort()[::-1]]
                matches = matches[np.unique(matches[:, 1], return_index=True)[1]]
                matches = matches[np.unique(matches[:, 0], return_index=True)[1]]
            correct[matches[:, 1].astype(int), i] = True
    return correct


_trapezoid = getattr(np, "trapezoid", None) or getattr(np, "trapz")


def _compute_ap(recall: np.ndarray, precision: np.ndarray) -> float:
    """101-point interpolated AP, identical to ultralytics metrics.compute_ap."""
    mrec = np.concatenate(([0.0], recall, [recall[-1] if len(recall) else 1.0], [1.0]))
    mpre = np.concatenate(([1.0], precision, [0.0], [0.0]))
    mpre = np.flip(np.maximum.accumulate(np.flip(mpre)))
    x = np.linspace(0, 1, 101)
    return float(_trapezoid(np.interp(x, mrec, mpre), x))


def _ap_per_class(tp, conf, pred_cls, target_cls, eps: float = 1e-16):
    """AP matrix (n_gt_classes, n_iou) and its classes; same as ultralytics ap_per_class."""
    i = np.argsort(-conf)
    tp, conf, pred_cls = tp[i], conf[i], pred_cls[i]
    unique_classes, nt = np.unique(target_cls, return_counts=True)
    ap = np.zeros((unique_classes.shape[0], tp.shape[1]))
    for ci, c in enumerate(unique_classes):
        i = pred_cls == c
        n_l = nt[ci]
        n_p = i.sum()
        if n_p == 0 or n_l == 0:
            continue
        fpc = (1 - tp[i]).cumsum(0)
        tpc = tp[i].cumsum(0)
        recall = tpc / (n_l + eps)
        precision = tpc / (tpc + fpc)
        for j in range(tp.shape[1]):
            ap[ci, j] = _compute_ap(recall[:, j], precision[:, j])
    return ap, unique_classes


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _iou_thresholds(iou_start, iou_stop, iou_step) -> np.ndarray:
    n = int(round((iou_stop - iou_start) / iou_step)) + 1
    return np.linspace(iou_start, iou_stop, n)


def _collect_stats(gt_strings, pred_strings, image_ids, iouv, max_dets):
    """Per-image matching; returns concatenated (tp, conf, pred_cls, target_cls)."""
    tps, confs, pcls, tcls = [], [], [], []
    for image_id, gt_s, pred_s in zip(image_ids, gt_strings, pred_strings):
        gt = _parse_boxes(gt_s, 5, image_id, ValueError, "Solution")
        pred = _parse_boxes(pred_s, 6, image_id, ParticipantVisibleError, PRED_COL)
        if len(pred) > max_dets:
            pred = pred[np.argsort(-pred[:, 1], kind="stable")[:max_dets]]

        gt_cls = gt[:, 0]
        tcls.append(gt_cls)
        if len(pred) == 0:
            continue
        pred_box = np.clip(_cxcywh_to_xyxy(pred[:, 2:6]), 0.0, 1.0)
        correct = np.zeros((len(pred), len(iouv)), dtype=bool)
        if len(gt):
            iou = _box_iou_xyxy(_cxcywh_to_xyxy(gt[:, 1:5]), pred_box)
            correct = _match_predictions(pred[:, 0], gt_cls, iou, iouv)
        tps.append(correct)
        confs.append(pred[:, 1])
        pcls.append(pred[:, 0])

    n_iou = len(iouv)
    tp = np.concatenate(tps) if tps else np.zeros((0, n_iou), dtype=bool)
    conf = np.concatenate(confs) if confs else np.zeros(0)
    pred_cls = np.concatenate(pcls) if pcls else np.zeros(0)
    target_cls = np.concatenate(tcls) if tcls else np.zeros(0)
    return tp, conf, pred_cls, target_cls


def _align(solution: pd.DataFrame, submission: pd.DataFrame, row_id_column_name: str) -> pd.DataFrame:
    """Return the solution with the participant's PredictionString attached as '_pred'."""
    if row_id_column_name not in submission.columns:
        raise ParticipantVisibleError(f"Submission is missing the '{row_id_column_name}' column.")
    if PRED_COL not in submission.columns:
        raise ParticipantVisibleError(f"Submission is missing the '{PRED_COL}' column.")
    sub = submission[[row_id_column_name, PRED_COL]].copy()
    sub[row_id_column_name] = sub[row_id_column_name].astype(str)
    dup = sub[row_id_column_name].duplicated()
    if dup.any():
        example = sub.loc[dup, row_id_column_name].iloc[0]
        raise ParticipantVisibleError(
            f"Submission has {int(dup.sum())} duplicated {row_id_column_name} values (e.g. '{example}'). "
            "Use one row per image with all of its boxes in a single PredictionString."
        )
    sol = solution.copy()
    sol[row_id_column_name] = sol[row_id_column_name].astype(str)
    missing = ~sol[row_id_column_name].isin(sub[row_id_column_name])
    if missing.any():
        example = sol.loc[missing, row_id_column_name].iloc[0]
        raise ParticipantVisibleError(
            f"Submission is missing {int(missing.sum())} test images (e.g. '{example}'). "
            "Include every image_id from sample_submission.csv, with PredictionString 'none' "
            "if there are no detections."
        )
    # Extra ids are ignored: Kaggle may pass the full submission with a Public/Private subset.
    sub = sub.rename(columns={PRED_COL: "_pred"})
    return sol.merge(sub, on=row_id_column_name, how="left")


def _map_from_frame(df, row_id_column_name, iouv, max_dets):
    tp, conf, pred_cls, target_cls = _collect_stats(
        df[PRED_COL].tolist(), df["_pred"].tolist(), df[row_id_column_name].tolist(), iouv, max_dets
    )
    if target_cls.size == 0:
        return np.zeros((0, len(iouv))), np.zeros(0)
    return _ap_per_class(tp, conf, pred_cls, target_cls)


def score(
    solution: pd.DataFrame,
    submission: pd.DataFrame,
    row_id_column_name: str,
    iou_start: float = 0.5,
    iou_stop: float = 0.95,
    iou_step: float = 0.05,
    max_dets: int = 100,
    primary: str = "map50_95",
) -> float:
    """XWOD leaderboard score: mAP50-95 (or mAP50 with primary='map50').

    Kaggle calls this separately for the Public and Private rows of the solution.

    >>> sol = pd.DataFrame({
    ...     "image_id": ["a", "b"],
    ...     "PredictionString": ["1 0.5 0.5 0.2 0.2", "0 0.3 0.3 0.1 0.2"],
    ... })
    >>> perfect = pd.DataFrame({
    ...     "image_id": ["a", "b"],
    ...     "PredictionString": ["1 0.9 0.5 0.5 0.2 0.2", "0 0.8 0.3 0.3 0.1 0.2"],
    ... })
    >>> round(score(sol, perfect, "image_id"), 4)   # Ultralytics-style AP tops out at 0.995
    0.995
    >>> empty = pd.DataFrame({"image_id": ["a", "b"], "PredictionString": ["none", "none"]})
    >>> score(sol, empty, "image_id")
    0.0
    """
    if primary not in ("map50_95", "map50"):
        raise ValueError(f"Unknown primary metric '{primary}'.")
    iouv = _iou_thresholds(iou_start, iou_stop, iou_step)
    df = _align(solution, submission, row_id_column_name)
    ap, _ = _map_from_frame(df, row_id_column_name, iouv, int(max_dets))
    if ap.size == 0:
        return 0.0
    return float(ap[:, 0].mean() if primary == "map50" else ap.mean())


def evaluate(
    solution: pd.DataFrame,
    submission: pd.DataFrame,
    row_id_column_name: str = "image_id",
    max_dets: int = 100,
) -> dict:
    """Detailed local report: overall, per-class, per-weather and per-Usage mAP."""
    iouv = _iou_thresholds(0.5, 0.95, 0.05)
    df = _align(solution, submission, row_id_column_name)

    def summary(frame):
        ap, classes = _map_from_frame(frame, row_id_column_name, iouv, max_dets)
        if ap.size == 0:
            return {"mAP50": 0.0, "mAP50-95": 0.0, "images": len(frame)}, {}
        per_class = {
            CLASS_NAMES[int(c)]: {"AP50": float(ap[k, 0]), "AP50-95": float(ap[k].mean())}
            for k, c in enumerate(classes)
        }
        return {"mAP50": float(ap[:, 0].mean()), "mAP50-95": float(ap.mean()), "images": len(frame)}, per_class

    overall, per_class = summary(df)
    report = {"overall": overall, "per_class": per_class}
    for col, key in ((WEATHER_COL, "per_weather"), (USAGE_COL, "per_usage")):
        if col in df.columns:
            report[key] = {str(v): summary(g)[0] for v, g in df.groupby(col, sort=True)}
    return report
