# fine-tune a COCO-pretrained YOLO (PyTorch, via ultralytics) on XWOD
#   python train.py                                dev run: train split only, scored on valid every epoch
#   python train.py --full --close-mosaic 0        final run: train + 75% of valid, the other 25% picks best.pt
#   python train.py --resume runs/<name>           continue an interrupted run

import argparse
import os
import random
from pathlib import Path
from ultralytics import YOLO
from common import CLASSES, HERE, RUNS, TRAIN_DIR, VALID_DIR, WEATHERS, WEIGHTS, list_images, weather_of

# rtx 3050 (6 GB, ~1.6 GB taken by the desktop): yolo26s @ 960 / batch 4 peaks at ~2.9 GB, ~9.5 min per train-only epoch
# going over the vram limit doesn't crash on windows, it silently spills into system ram & runs ~4x slower
MODEL = "yolo26s.pt"
IMGSZ = 960            # 28% of train boxes are < 32 px at 640, 14% at 960
BATCH = 4              # ultralytics accumulates gradients up to an effective batch of 64 (nbs)
EPOCHS = 40
WORKERS = 8
SEED = 42
# dev run (close_mosaic 10): valid peaked at epoch 27-29 (0.347) & sat ~0.012 lower once mosaic was switched off,
# so the final run keeps mosaic on to the end & relies on a held-out slice of valid to pick the best epoch
HOLDOUT = 0.25


def fix_mixed_labels():
    # ultralytics 8.4 throws away a label file that mixes polygon & box rows (valid/flooding_valid_00864.txt),
    # so turn polygon rows into their bounding box once; the original is kept next to it as .txt.orig
    for f in (f for s in ("train", "valid") for f in (HERE / s / "labels").glob("*.txt")):
        rows = [line.split() for line in f.read_text().splitlines() if line.strip()]
        if not any(len(r) > 5 for r in rows):
            continue
        out = []
        for r in rows:
            v = [float(x) for x in r]
            if len(v) > 5:
                xs, ys = v[1::2], v[2::2]
                v = [v[0], (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(xs) - min(xs), max(ys) - min(ys)]
            out.append(f"{int(v[0])} " + " ".join(f"{x:.6f}" for x in v[1:]))
        f.with_suffix(".txt.orig").write_text(f.read_text())
        f.write_text("\n".join(out) + "\n")
        print(f"converted polygon rows to boxes in {f.name}")


def write_full_split(holdout):
    # train = all of train + most of valid; val = a weather-stratified slice of valid used only to pick best.pt
    rng = random.Random(SEED)
    valid = list_images(VALID_DIR)
    hold = []
    for w in WEATHERS:
        group = [p for p in valid if weather_of(p.name) == w]
        rng.shuffle(group)
        hold += group[:round(len(group) * holdout)]
    hold_set = set(hold)
    train = list_images(TRAIN_DIR) + [p for p in valid if p not in hold_set]
    out = RUNS / "splits"
    out.mkdir(parents=True, exist_ok=True)
    (out / "full_train.txt").write_text("\n".join(map(str, train)) + "\n")
    (out / "full_holdout.txt").write_text("\n".join(map(str, sorted(hold))) + "\n")
    yaml = out / "full.yaml"
    yaml.write_text("\n".join([f"train: {out / 'full_train.txt'}", f"val: {out / 'full_holdout.txt'}", "names:"]
                              + [f"  {i}: {n}" for i, n in enumerate(CLASSES)]) + "\n")
    print(f"full split: {len(train)} train images, {len(hold)} holdout images")
    return yaml


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--imgsz", type=int, default=IMGSZ)
    ap.add_argument("--batch", type=int, default=BATCH)
    ap.add_argument("--epochs", type=int, default=EPOCHS)
    ap.add_argument("--workers", type=int, default=WORKERS)
    ap.add_argument("--close-mosaic", type=int, default=10, help="epochs at the end without mosaic (dev run used 10)")
    ap.add_argument("--full", action="store_true", help="train on train + valid (minus the holdout)")
    ap.add_argument("--holdout", type=float, default=HOLDOUT, help="share of valid kept out to pick best.pt")
    ap.add_argument("--name")
    ap.add_argument("--resume", help="run folder to resume")
    args = ap.parse_args()

    os.chdir(WEIGHTS)   # ultralytics drops helper downloads (amp check model) into the cwd
    if args.resume:
        YOLO(Path(args.resume).resolve() / "weights" / "last.pt").train(resume=True)
        return

    fix_mixed_labels()
    data = write_full_split(args.holdout) if args.full else HERE / "data.yaml"
    name = args.name or f"{Path(args.model).stem}_{args.imgsz}_{'full' if args.full else 'dev'}"
    YOLO(WEIGHTS / args.model).train(
        data=str(data),
        imgsz=args.imgsz,
        batch=args.batch,
        epochs=args.epochs,
        workers=args.workers,
        seed=SEED,
        project=str(RUNS),
        name=name,
        exist_ok=True,
        close_mosaic=args.close_mosaic,
    )


if __name__ == "__main__":
    main()
