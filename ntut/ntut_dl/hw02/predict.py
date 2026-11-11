# predict with a trained model
#   python predict.py <weights.pt> --split valid [--imgsz 960] [--augment]    score on valid with the leaderboard metric
#   python predict.py <weights.pt> --split holdout ...                         same, on the valid slice the --full run never trained on
#   python predict.py <weights.pt> --split test --out submissions/name.csv    write a kaggle submission

import argparse
from pathlib import Path
import pandas as pd
from ultralytics import YOLO
import xwod_map
from common import RUNS, SUBMISSIONS, TEST_DIR, VALID_DIR, labels_to_solution, list_images, predict_folder


def score_valid(pred, src):
    report = xwod_map.evaluate(labels_to_solution(src), pred)
    o = report["overall"]
    print(f"\nvalid mAP50-95 {o['mAP50-95']:.4f}   mAP50 {o['mAP50']:.4f}   (leaderboard metric)")
    print(pd.DataFrame(report["per_class"]).T.round(4).to_string())
    w = pd.DataFrame(report["per_weather"]).T
    print(w[["images", "mAP50", "mAP50-95"]].astype({"images": int, "mAP50": float, "mAP50-95": float})
          .round(4).sort_values("mAP50-95").to_string())
    return o["mAP50-95"]


def check_submission(sub):
    ids = {p.stem for p in list_images(TEST_DIR)}
    assert sub["image_id"].is_unique, "duplicate image_id rows"
    assert set(sub["image_id"]) == ids, "image_ids don't match test/images"
    assert (sub["PredictionString"].str.len() > 0).all(), "empty cells"
    n = sub["PredictionString"].map(lambda s: 0 if s == "none" else len(s.split()) // 6)
    assert n.max() <= 100
    print(f"{len(sub)} images, {n.sum()} boxes, {(n == 0).sum()} with 'none'")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("weights")
    ap.add_argument("--split", choices=["valid", "holdout", "test"], default="valid")
    ap.add_argument("--imgsz", type=int, default=960)
    ap.add_argument("--augment", action="store_true", help="test-time augmentation (flips + rescales)")
    ap.add_argument("--out", help="csv path for the predictions")
    ap.add_argument("--device")
    args = ap.parse_args()

    model = YOLO(args.weights)
    src = {"valid": VALID_DIR, "test": TEST_DIR}.get(args.split)
    if args.split == "holdout":
        src = (RUNS / "splits" / "full_holdout.txt").read_text().splitlines()
    print(f"{args.weights} on {args.split}, imgsz {args.imgsz}, augment {args.augment}")
    pred = predict_folder(model, src, args.imgsz, augment=args.augment, device=args.device)

    if args.split != "test":
        score_valid(pred, src)
    else:
        check_submission(pred)
    out = Path(args.out) if args.out else (SUBMISSIONS / "submission.csv" if args.split == "test" else None)
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        pred.to_csv(out, index=False)
        print("saved", out)


if __name__ == "__main__":
    main()
