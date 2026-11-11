# runs on kaggle's free 2x T4 (16 GB each): train a bigger YOLO on all labeled XWOD data & predict test
# push from hw02 with:   python -m kaggle kernels push -p kaggle_kernel --accelerator NvidiaTeslaT4
# MODE "pilot" times a few model / imgsz configs (~20 min); MODE "train" is the real run (fits kaggle's 12 h cap)
# standalone on purpose: kaggle can't import common.py / train.py, so the label fix is repeated here

MODE = "train"
MODEL = "yolo26l.pt"
IMGSZ = 1280
# total over both GPUs (4 per GPU). on a 14.6 GB T4 at 1280, 8 per GPU runs out of memory (single-GPU ultralytics
# hides that by silently halving the batch, DDP just crashes) and 6 per GPU hit 14.1 GB in the first forward pass
BATCH = 8
HOURS = 10.5           # training budget; kaggle kills a session at 12 h, the rest is setup + test prediction
# (model, imgsz, per-GPU batch) timed on one GPU in pilot mode
PILOT = [("yolo26m.pt", 1280, 8), ("yolo26l.pt", 1280, 8), ("yolo26m.pt", 960, 8)]

import gc
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

WORK = Path("/kaggle/working")
DATA = WORK / "data"
CLASSES = ["person", "car", "truck", "motorcycle", "bus", "bike"]
CONF, MAX_DET = 0.001, 100   # keep low-confidence boxes; the scorer only reads the top 100 per image


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def find_data_root():
    for pattern in ("*/data.yaml", "*/*/data.yaml", "*/*/*/data.yaml"):
        hits = sorted(Path("/kaggle/input").glob(pattern))
        if hits:
            return hits[0].parent
    raise FileNotFoundError("competition data not found under /kaggle/input")


def fix_label(text):
    # polygon rows -> their bounding box (ultralytics 8.4 drops a file that mixes polygon & box rows)
    out = []
    for line in text.splitlines():
        v = line.split()
        if len(v) > 5:
            f = [float(x) for x in v]
            xs, ys = f[1::2], f[2::2]
            v = [v[0]] + [f"{x:.6f}" for x in ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2,
                                                max(xs) - min(xs), max(ys) - min(ys))]
        if v:
            out.append(" ".join(v))
    return "\n".join(out) + "\n" if out else ""


def resize_one(job):
    # shrink to the training size once, so the 4 kaggle cpus don't decode 2560 px jpegs every epoch
    import cv2
    src, dst, max_side = job
    im = cv2.imread(str(src))   # applies exif orientation, same as ultralytics reading the original
    if im is None:
        raise ValueError(f"can't read {src}")
    h, w = im.shape[:2]
    r = max_side / max(h, w)
    if r < 1:
        im = cv2.resize(im, (round(w * r), round(h * r)), interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(dst), im, [cv2.IMWRITE_JPEG_QUALITY, 95])


def prepare(root, max_side):
    jobs = []
    for split in ("train", "valid"):
        for sub in ("images", "labels"):
            (DATA / split / sub).mkdir(parents=True, exist_ok=True)
        for lab in (root / split / "labels").glob("*.txt"):
            (DATA / split / "labels" / lab.name).write_text(fix_label(lab.read_text()))
        jobs += [(p, DATA / split / "images" / p.name, max_side) for p in (root / split / "images").iterdir()]
    with ProcessPoolExecutor(os.cpu_count()) as ex:
        list(ex.map(resize_one, jobs, chunksize=16))
    yaml = DATA / "all.yaml"
    yaml.write_text(f"path: {DATA}\ntrain: [train/images, valid/images]\nval: valid/images\nnames:\n"
                    + "".join(f"  {i}: {n}\n" for i, n in enumerate(CLASSES)))
    log(f"prepared {len(jobs)} images at max side {max_side}")
    return yaml


class Stop(Exception):
    pass


def bench(yaml, model_name, imgsz, batch, n=50):
    import torch
    from ultralytics import YOLO
    t = []

    def on_batch_end(trainer):
        t.append(time.perf_counter())
        if len(t) == n:
            raise Stop

    model = YOLO(model_name)
    model.add_callback("on_train_batch_end", on_batch_end)
    torch.cuda.init()
    torch.cuda.reset_peak_memory_stats(0)
    tag = f"{model_name} imgsz={imgsz} batch/gpu={batch}"
    try:
        model.train(data=str(yaml), imgsz=imgsz, batch=batch, epochs=1, device=0, workers=4, val=False,
                    plots=False, project=str(WORK / "bench"), name="b", exist_ok=True, verbose=False)
    except Stop:
        dt = (t[-1] - t[10]) / (len(t) - 11)
        mem = torch.cuda.max_memory_reserved(0) / 2**30
        # 2 GPUs at ~90% scaling, train + valid = 7689 images
        epoch_min = 7689 / (2 * 0.9 * batch / dt) / 60
        log(f"PILOT {tag}: {dt:.3f} s/it, {batch / dt:.1f} img/s per GPU, peak {mem:.1f} GiB, "
            f"~{epoch_min:.1f} min/epoch on 2 GPUs -> ~{HOURS * 60 / epoch_min:.0f} epochs in {HOURS} h")
    except torch.OutOfMemoryError:
        log(f"PILOT {tag}: OOM")
    del model
    gc.collect()
    torch.cuda.empty_cache()


def predict_test(weights, root, imgsz, augment, out):
    import pandas as pd
    from ultralytics import YOLO
    model = YOLO(weights)
    files = sorted(str(p) for p in (root / "test" / "images").iterdir())
    rows = []
    for i in range(0, len(files), 8):
        chunk = files[i:i + 8]
        # results come back in input order (r.path is image0.jpg, ...), so pair them by position
        for f, r in zip(chunk, model.predict(chunk, imgsz=imgsz, conf=CONF, max_det=MAX_DET, augment=augment,
                                              device=0, verbose=False)):
            b = r.boxes
            s = " ".join(f"{int(c)} {p:.5f} {x:.6f} {y:.6f} {w:.6f} {h:.6f}"
                         for c, p, (x, y, w, h) in zip(b.cls.tolist(), b.conf.tolist(), b.xywhn.tolist()))
            rows.append((Path(f).stem, s or "none"))
    pd.DataFrame(rows, columns=["image_id", "PredictionString"]).to_csv(out, index=False)
    log(f"wrote {out} ({len(rows)} rows)")


def main():
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "ultralytics==8.4.208"], check=True)
    import torch
    log("python", sys.version.split()[0], "| torch", torch.__version__, "| cpus", os.cpu_count(),
        "| gpus", [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())])
    subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv"])
    root = find_data_root()
    log("data root", root)
    os.chdir(WORK)

    if MODE == "pilot":
        yaml = prepare(root, max(c[1] for c in PILOT))
        for cfg in PILOT:
            bench(yaml, *cfg)
        # short real 2-GPU run to make sure DDP works here (look for its it/s in the log)
        from ultralytics import YOLO
        t0 = time.time()
        YOLO(MODEL).train(data=str(yaml), imgsz=IMGSZ, batch=BATCH, epochs=1, fraction=0.15, device=[0, 1],
                          workers=4, val=False, plots=False, project=str(WORK / "bench"), name="ddp", exist_ok=True)
        log(f"PILOT ddp {MODEL} imgsz={IMGSZ} batch={BATCH}, 15% of an epoch incl. startup: {time.time() - t0:.0f} s")
    else:
        from ultralytics import YOLO
        yaml = prepare(root, IMGSZ)
        YOLO(MODEL).train(
            data=str(yaml), imgsz=IMGSZ, batch=BATCH, epochs=300, time=HOURS, device=[0, 1], workers=4, seed=42,
            project=str(WORK / "runs"), name="main", exist_ok=True,
            close_mosaic=0,   # locally the score dropped once mosaic switched off, so keep it on to the end
            val=False,        # valid is part of the training data here, per-epoch scores would mean nothing
        )
        last = WORK / "runs" / "main" / "weights" / "last.pt"
        shutil.copy(last, WORK / f"{Path(MODEL).stem}_{IMGSZ}_last.pt")
        for size in (IMGSZ, IMGSZ * 5 // 4):   # TTA scales (1, 0.83, 0.67) of each; pick between them on the leaderboard
            predict_test(last, root, size, True, WORK / f"sub_{Path(MODEL).stem}_{IMGSZ}_tta{size}.csv")

    shutil.rmtree(DATA, ignore_errors=True)   # keep the downloadable output small
    shutil.rmtree(WORK / "bench", ignore_errors=True)
    log("done")


if __name__ == "__main__":
    try:
        main()
    finally:   # even after a crash, so the kernel output never carries the 1 GB data copy
        shutil.rmtree(DATA, ignore_errors=True)
        shutil.rmtree(WORK / "bench", ignore_errors=True)
