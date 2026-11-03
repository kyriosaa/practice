# fine-tune YOLO11 on AR Traffic Objects (mostly AR renders) & check it on real photos

import sys
from pathlib import Path
from ultralytics import YOLO

MODEL = "yolo11s.pt"   # COCO-pretrained starting point
IMGSZ = 1024           # objects are tiny (often ~1% of the image width), so go above the default 640
BATCH = 8
HOURS = 1.0            # ultralytics fits the whole lr schedule into this time budget
WORKERS = 8
SEED = 42

EXAM = Path(r"F:\engineering\practice\ntut\ntut_dl\exam01")
DATA = EXAM / "data"                        # unzipped kuantinglai/ar-traffic-objects
NAMES = ["cone", "delineator", "jersey_barrier", "curve_mirror", "transformer_box", "fence"]

def write_data_yaml():
    # train on every AR render + every real photo; validate on the real photos in valid/
    # test/real is the competition test set, so it never goes into training or validation
    train = sorted(str(p) for p in (DATA / "train").glob("*/*") if p.is_dir())
    val = [str(DATA / "valid" / "real")]
    lines = ["train:"] + [f"  - {p}" for p in train]
    lines += ["val:"] + [f"  - {p}" for p in val]
    lines += ["names:"] + [f"  {i}: {n}" for i, n in enumerate(NAMES)]
    path = EXAM / "data" / "data.yaml"
    path.write_text("\n".join(lines) + "\n")
    print(path.read_text())
    return path

def main():
    data = write_data_yaml()
    model = YOLO(EXAM / "weights" / MODEL)
    model.train(
        data=str(data),
        imgsz=IMGSZ,
        batch=BATCH,
        time=HOURS,
        epochs=100,            # ignored once time= is set
        workers=WORKERS,
        seed=SEED,
        project=str(EXAM / "runs"),
        name=sys.argv[1] if len(sys.argv) > 1 else "yolo11s",
        exist_ok=True,
        cos_lr=True,
        close_mosaic=2,
        # AR renders look cleaner than real photos, so push colour/scale jitter a bit harder
        hsv_h=0.02, hsv_s=0.7, hsv_v=0.5,
        scale=0.6,
        mixup=0.1,
        plots=False,
    )

if __name__ == "__main__":
    main()
