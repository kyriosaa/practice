# predict the real test photos & write the competition submission.csv

import json
import sys
from pathlib import Path
import pandas as pd
from ultralytics import YOLO

IMGSZ = 1024
AUGMENT = True         # test-time augmentation (flip + rescale): holdout mAP50-95 0.571 -> 0.598
CONF = 0.001           # keep low-confidence boxes, mAP only cares about the ranking
MAX_DET = 100          # the scorer only looks at the top 100 boxes per image

EXAM = Path(r"F:\engineering\practice\ntut\ntut_dl\exam01")
TEST = EXAM / "data" / "test" / "real" / "images"
# public test filename -> competition image_id, from the professor's public_to_competition_ids notebook
ID_MAP = EXAM / "data" / "public_to_competition_ids.json"

def load_id_map():
    return json.loads(ID_MAP.read_text())

def main():
    weights = sys.argv[1]
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else EXAM / "submission.csv"
    device = sys.argv[3] if len(sys.argv) > 3 else None   # e.g. "cpu" while the gpu is busy training
    model = YOLO(weights)
    id_map = load_id_map()
    files = sorted(str(f) for f in TEST.glob("*") if f.suffix.lower() in (".jpg", ".jpeg", ".png"))
    rows, n_boxes = [], 0
    for i in range(0, len(files), 16):
        batch = files[i:i + 16]
        # results come back in input order, so pair them with the filenames by position
        for f, r in zip(batch, model.predict(batch, imgsz=IMGSZ, conf=CONF, max_det=MAX_DET,
                                                             augment=AUGMENT, device=device, verbose=False)):
            b = r.boxes
            s = " ".join(f"{int(c)} {p:.4f} {x:.6f} {y:.6f} {w:.6f} {h:.6f}"
                         for c, p, (x, y, w, h) in zip(b.cls.tolist(), b.conf.tolist(), b.xywhn.tolist()))
            n_boxes += len(b)
            rows.append((id_map[Path(f).stem], s or "none"))
    df = pd.DataFrame(rows, columns=["image_id", "PredictionString"]).sort_values("image_id")
    assert len(df) == len(id_map) and df["image_id"].is_unique
    df.to_csv(out, index=False)
    print(f"wrote {len(rows)} rows ({n_boxes} boxes) to {out}")

if __name__ == "__main__":
    main()
