# train a small CNN model on EMNIST ByClass (62 classes) & write submission.csv

import time
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset, random_split

EPOCHS = 5             # how many full passes over the training data
BATCH_SIZE = 256       # how many images the model sees before each weight update
LEARNING_RATE = 1e-3   # how big each update step is
VAL_FRACTION = 0.1     # keep 10% of the training data aside to measure progress honestly
QUICK_TEST = False     # True = train on 20,000 images for 1 epoch, just to check everything runs
SEED = 42              # makes the random parts repeatable

KAGGLE_DATASET = "darkfanxing/ntutemnist"
TRAIN_NAME = "emnist-byclass-train.npz"
TEST_NAME = "emnist-byclass-test.npz"
HERE = Path(__file__).resolve().parent     # the folder this script is in
NUM_CLASSES = 62

# device
def pick_device():
    if torch.cuda.is_available():            # NVIDIA
        return torch.device("cuda")
    # if torch.backends.mps.is_available():    # apple
    #     return torch.device("mps")
    return torch.device("cpu")               # anything but slower

# load data
def to_uint8_images(x):
    # return img as uint8 0-255 w/ shape (N, 1, 28, 28)
    x = np.asarray(x)
    if x.dtype != np.uint8:
        if x.max() <= 1.0:                   # already scaled to 0-1
            x = x * 255.0
        x = x.clip(0, 255).astype(np.uint8)
    return x.reshape(len(x), 1, 28, 28)     # 1 = one color channel (grayscale)

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
    train_file = _find_npz(folder, TRAIN_NAME, "train")
    test_file = _find_npz(folder, TEST_NAME, "test")
    if train_file is None or test_file is None:
        found = [str(p.relative_to(folder)) for p in folder.rglob("*") if p.is_file()]
        raise FileNotFoundError(f"Couldn't find the train/test .npz files. Files downloaded: {found}")
    return train_file, test_file

def load_data():
    train_file, test_file = find_data_files()
    train = np.load(train_file)
    x = to_uint8_images(train["training_images"])
    y = train["training_labels"].reshape(-1).astype(np.int64)  # loss function wants int64
    x_test = to_uint8_images(np.load(test_file)["testing_images"])

    if QUICK_TEST:
        x, y = x[:20_000], y[:20_000]

    print(f"Training images: {x.shape}, labels: {y.shape}, test images: {x_test.shape}")
    return torch.from_numpy(x), torch.from_numpy(y), torch.from_numpy(x_test)

# model is a simple convolutional neural network
class SimpleCNN(nn.Module):
    def __init__(self, num_classes=NUM_CLASSES):
        super().__init__()
        # "features" learns to detect strokes, curves, corners, etc etc
        self.features = nn.Sequential(
            # 1x28x28 -> 32x28x28 -> 32x14x14
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            # 32x14x14 -> 64x14x14 -> 64x7x7
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        # "classifier" turns those features into 62 scores w/ one per class
        self.classifier = nn.Sequential(
            nn.Flatten(),                     # 64x7x7 -> 3136 numbers
            nn.Linear(64 * 7 * 7, 256),
            nn.ReLU(),
            nn.Dropout(0.3),                  # randomly drop 30% during training to reduce overfitting
            nn.Linear(256, num_classes),      # 62 outputs ("logits")
        )

    def forward(self, x):
        return self.classifier(self.features(x))

def prepare(images, device):
    """uint8 0-255 -> float 0-1, on the right device."""
    return images.to(device).float() / 255.0

# training & eval loops
def train_one_epoch(model, loader, loss_fn, optimizer, device):
    model.train()                             
    total_loss, correct, seen = 0.0, 0, 0
    for step, (images, labels) in enumerate(loader, start=1):
        images, labels = prepare(images, device), labels.to(device)

        outputs = model(images)               
        loss = loss_fn(outputs, labels)       

        optimizer.zero_grad()                 
        loss.backward()                      
        optimizer.step()                      

        total_loss += loss.item() * len(labels)
        correct += (outputs.argmax(dim=1) == labels).sum().item()
        seen += len(labels)
        if step % 200 == 0 or step == len(loader):
            print(f"    batch {step}/{len(loader)}  loss {total_loss / seen:.4f}  "
                  f"acc {correct / seen:.2%}", end="\r")
    print()
    return total_loss / seen, correct / seen

# no need for gradients when evaluating
@torch.no_grad()                              
def evaluate(model, loader, loss_fn, device):
    model.eval()
    total_loss, correct, seen = 0.0, 0, 0
    for images, labels in loader:
        images, labels = prepare(images, device), labels.to(device)
        outputs = model(images)
        total_loss += loss_fn(outputs, labels).item() * len(labels)
        correct += (outputs.argmax(dim=1) == labels).sum().item()
        seen += len(labels)
    return total_loss / seen, correct / seen

@torch.no_grad()
def predict(model, images, device):
    model.eval()
    loader = DataLoader(TensorDataset(images), batch_size=1024, shuffle=False)
    predictions = []
    for (batch,) in loader:
        outputs = model(prepare(batch, device))
        predictions.append(outputs.argmax(dim=1).cpu())
    return torch.cat(predictions).numpy()

def write_submission(predictions, path=HERE / "submission.csv"):
    with open(path, "w", newline="") as f:
        f.write("Id,Category\n")
        for i, label in enumerate(predictions):
            f.write(f"{i},{label}\n")
    print(f"Wrote {len(predictions)} predictions to {path}")

def main():
    torch.manual_seed(SEED)
    device = pick_device()
    print(f"Using device: {device}")

    x, y, x_test = load_data()

    # 90%-10%
    # 90 to learn from and 10 to validate
    full = TensorDataset(x, y)
    n_val = int(len(full) * VAL_FRACTION)
    train_set, val_set = random_split(
        full, [len(full) - n_val, n_val], generator=torch.Generator().manual_seed(SEED)
    )
    train_loader = DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=1024, shuffle=False)
    print(f"Train: {len(train_set)} images, validation: {len(val_set)} images")

    model = SimpleCNN().to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Model has {n_params:,} trainable numbers (parameters)")

    loss_fn = nn.CrossEntropyLoss()           # the standard loss for "pick one of N classes"
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    epochs = 1 if QUICK_TEST else EPOCHS
    best_val_acc = 0.0
    for epoch in range(1, epochs + 1):
        start = time.time()
        print(f"Epoch {epoch}/{epochs}")
        train_loss, train_acc = train_one_epoch(model, train_loader, loss_fn, optimizer, device)
        val_loss, val_acc = evaluate(model, val_loader, loss_fn, device)
        print(f"  train loss {train_loss:.4f} acc {train_acc:.2%} | "
              f"val loss {val_loss:.4f} acc {val_acc:.2%} | {time.time() - start:.0f}s")

        if val_acc > best_val_acc:            # keep the best version of the model
            best_val_acc = val_acc
            torch.save(model.state_dict(), HERE / "model.pt")
            print(f"  saved new best model (val acc {val_acc:.2%})")

    # reload the best weights and predict the official test images
    model.load_state_dict(torch.load(HERE / "model.pt", map_location=device))
    predictions = predict(model, x_test, device)
    write_submission(predictions)
    print(f"Done. Best validation accuracy: {best_val_acc:.2%} "
          f"(random guessing would be ~{1 / NUM_CLASSES:.1%})")

if __name__ == "__main__":
    main()