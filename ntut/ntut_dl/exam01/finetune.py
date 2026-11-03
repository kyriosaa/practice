# second stage: fine-tune the AR-trained model on real photos only
# (train/real + 80% of valid/real; the other 20% of valid/real stays held out to measure the gain)

import random
import sys
from pathlib import Path
from ultralytics import YOLO

IMGSZ = 1024
BATCH = 8
HOURS = float(sys.argv[2]) if len(sys.argv) > 2 else 0.27
HOLDOUT = 0.2
SEED = 42

EXAM = Path(r"F:\engineering\practice\ntut\ntut_dl\exam01")
DATA = EXAM / "data"
NAMES = ["cone", "delineator", "jersey_barrier", "curve_mirror", "transformer_box", "fence"]
IMG_EXTS = (".jpg", ".jpeg", ".png")

def images(folder):
    return sorted(str(p) for p in folder.rglob("*") if p.suffix.lower() in IMG_EXTS)

def write_split():
    valid = images(DATA / "valid" / "real")
    random.Random(SEED).shuffle(valid)
    n_hold = int(len(valid) * HOLDOUT)
    hold, valid_train = sorted(valid[:n_hold]), valid[n_hold:]
    train = images(DATA / "train" / "real") + sorted(valid_train)
    (DATA / "ft_train.txt").write_text("\n".join(train) + "\n")
    (DATA / "ft_holdout.txt").write_text("\n".join(hold) + "\n")
    yaml = DATA / "ft.yaml"
    yaml.write_text("\n".join([f"train: {DATA / 'ft_train.txt'}", f"val: {DATA / 'ft_holdout.txt'}", "names:"]
                              + [f"  {i}: {n}" for i, n in enumerate(NAMES)]) + "\n")
    print(f"fine-tune train: {len(train)} images, holdout: {len(hold)} images")
    return yaml

def main():
    start = sys.argv[1]
    yaml = write_split()
    base = YOLO(start).val(data=str(yaml), imgsz=IMGSZ, batch=BATCH, conf=0.001, plots=False, verbose=False)
    print(f"BASELINE holdout mAP50-95 {base.box.map:.4f} mAP50 {base.box.map50:.4f}", flush=True)
    YOLO(start).train(
        data=str(yaml), imgsz=IMGSZ, batch=BATCH, time=HOURS, epochs=100, workers=8, seed=SEED,
        project=str(EXAM / "runs"), name="finetune_real", exist_ok=True,
        optimizer="AdamW", lr0=0.0005, warmup_epochs=0.5, cos_lr=True, close_mosaic=1,
        hsv_h=0.02, hsv_s=0.7, hsv_v=0.5, scale=0.6, plots=False,
    )

if __name__ == "__main__":
    main()
