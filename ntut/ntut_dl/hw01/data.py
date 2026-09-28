# downloads the kagglehub files and prints

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

KAGGLE_DATASET = "darkfanxing/ntutemnist"
TRAIN_NAME = "emnist-byclass-train.npz"
TEST_NAME = "emnist-byclass-test.npz"
HERE = Path(__file__).resolve().parent     # the folder this script is in

# 0-9 are digits
# 10-35 are A-Z
# 36-61 are a-z
CLASSES = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

# EMNIST images are mirrored/rotated but it doesnt affect training
# set to True if u want orientation fixed
FIX_ORIENTATION = False

def _find_npz(folder, exact_name, keyword):
    exact = sorted(folder.rglob(exact_name))
    if exact:
        return exact[0]
    loose = [p for p in folder.rglob("*.npz") if keyword in p.name.lower()]
    return loose[0] if len(loose) == 1 else None

def find_data_files():
    if (HERE / TRAIN_NAME).exists() and (HERE / TEST_NAME).exists():
        print(f"Using data files in {HERE}")
        return HERE / TRAIN_NAME, HERE / TEST_NAME

    import kagglehub
    # reuses the copy saved in ~/.cache/kagglehub after the first download
    folder = Path(kagglehub.dataset_download(KAGGLE_DATASET))
    print(f"Using data files in {folder}")
    all_files = [str(p.relative_to(folder)) for p in folder.rglob("*") if p.is_file()]
    print("Files in the Kaggle dataset:", all_files)
    train_file = _find_npz(folder, TRAIN_NAME, "train")
    test_file = _find_npz(folder, TEST_NAME, "test")
    if train_file is None or test_file is None:
        raise FileNotFoundError("Couldn't find the train/test .npz files in the list above.")
    return train_file, test_file


def main():
    train_file, test_file = find_data_files()
    train = np.load(train_file)
    print("Arrays inside the training file:", train.files)
    x = train["training_images"]
    y = train["training_labels"].reshape(-1)

    x_test = np.load(test_file)["testing_images"]

    print(f"\ntraining_images: shape={x.shape}, dtype={x.dtype}, "
          f"min={x.min()}, max={x.max()}")
    print(f"training_labels: shape={y.shape}, dtype={y.dtype}, "
          f"min={y.min()}, max={y.max()}")
    print(f"testing_images:  shape={x_test.shape}, dtype={x_test.dtype}")

    counts = np.bincount(y, minlength=len(CLASSES))
    print("\nExamples per class (label: character = count):")
    for label, n in enumerate(counts):
        end = "\n" if label % 6 == 5 else "   "
        print(f"{label:2d}:{CLASSES[label]} = {n:6d}", end=end)
    print(f"\nMost common:  '{CLASSES[counts.argmax()]}' ({counts.max()})")
    print(f"Least common: '{CLASSES[counts.argmin()]}' ({counts.min()})")
    print(f"Random guessing would score about 1/62 = {1/62:.1%}")

    # show 32 random images with their labels
    rng = np.random.default_rng(0)
    idx = rng.choice(len(x), size=32, replace=False)
    fig, axes = plt.subplots(4, 8, figsize=(12, 6.5))
    for ax, i in zip(axes.flat, idx):
        img = x[i].reshape(28, 28)
        if FIX_ORIENTATION:
            img = img.T
        ax.imshow(img, cmap="gray")
        ax.set_title(f"{y[i]} = '{CLASSES[y[i]]}'", fontsize=10)
        ax.axis("off")
    fig.suptitle("Random training images (label number = character)")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()