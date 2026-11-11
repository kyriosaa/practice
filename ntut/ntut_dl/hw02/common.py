# shared paths & helpers for the XWOD (extreme weather object detection) kaggle comp

from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
TRAIN_DIR = HERE / "train" / "images"
VALID_DIR = HERE / "valid" / "images"
TEST_DIR = HERE / "test" / "images"
WEIGHTS = HERE / "weights"           # coco-pretrained starting points (yolo26s.pt, ...)
RUNS = HERE / "runs"                 # ultralytics training runs
SUBMISSIONS = HERE / "submissions"

CLASSES = ["person", "car", "truck", "motorcycle", "bus", "bike"]
WEATHERS = ["heavy_rain", "snow", "fog", "dust", "flooding", "tornado", "wildfire"]
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}   # some .jpg files are really webp/png, opencv handles it

CONF = 0.001     # keep low-confidence boxes, mAP only cares about the ranking
MAX_DET = 100    # the scorer only looks at the top 100 boxes per image


def weather_of(name):
    return next((w for w in WEATHERS if name.startswith(w + "_")), "unknown")


def list_images(folder):
    return sorted(p for p in Path(folder).iterdir() if p.suffix.lower() in IMG_EXTS)


def resolve_images(src):
    # a folder, or an explicit list of image paths (e.g. the holdout split)
    return list_images(src) if isinstance(src, (str, Path)) else [Path(p) for p in src]


def boxes_to_string(boxes):
    # one image's ultralytics boxes -> "cls conf cx cy w h ..." (normalized), or "none"
    if boxes is None or len(boxes) == 0:
        return "none"
    return " ".join(
        f"{int(c)} {p:.5f} {x:.6f} {y:.6f} {w:.6f} {h:.6f}"
        for c, p, (x, y, w, h) in zip(boxes.cls.tolist(), boxes.conf.tolist(), boxes.xywhn.tolist())
    )


def predict_folder(model, src, imgsz, augment=False, batch=8, device=None):
    # predict every image in a folder (or list) -> DataFrame in submission format
    files = [str(f) for f in resolve_images(src)]
    rows = []
    for i in range(0, len(files), batch):
        chunk = files[i:i + batch]
        results = model.predict(chunk, imgsz=imgsz, conf=CONF, max_det=MAX_DET, augment=augment,
                                device=device, verbose=False)
        # results come back in input order (r.path is image0.jpg, ...), so pair them by position
        rows += [(Path(f).stem, boxes_to_string(r.boxes)) for f, r in zip(chunk, results)]
        if (i // batch) % 50 == 0:
            print(f"  {min(i + batch, len(files))}/{len(files)} images", flush=True)
    return pd.DataFrame(rows, columns=["image_id", "PredictionString"])


def labels_to_solution(src):
    # yolo label files -> answer-key table (same as the professor's notebook, incl. polygon -> box & clipping)
    rows = []
    for img in resolve_images(src):
        lab = img.parent.parent / "labels" / f"{img.stem}.txt"
        if lab.with_suffix(".txt.orig").exists():   # score against the label file as kaggle shipped it
            lab = lab.with_suffix(".txt.orig")
        boxes = []
        for line in (lab.read_text().splitlines() if lab.exists() else []):
            v = [float(x) for x in line.split()]
            if len(v) == 5:
                c, cx, cy, w, h = v
            elif len(v) > 5:   # polygon -> its bounding box
                xs, ys = v[1::2], v[2::2]
                c, cx, cy, w, h = v[0], (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(xs) - min(xs), max(ys) - min(ys)
            else:
                continue
            x0, y0, x1, y1 = max(0, cx - w / 2), max(0, cy - h / 2), min(1, cx + w / 2), min(1, cy + h / 2)
            boxes.append(f"{int(c)} {(x0 + x1) / 2:.10g} {(y0 + y1) / 2:.10g} {x1 - x0:.10g} {y1 - y0:.10g}")
        rows.append((img.stem, " ".join(boxes) or "none", weather_of(img.name)))
    return pd.DataFrame(rows, columns=["image_id", "PredictionString", "weather"])
