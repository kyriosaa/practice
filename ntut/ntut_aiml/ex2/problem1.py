# problem 1

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "ex_q" / "data1.csv"
PLOT_FILE = HERE / "submit" / "plt1_pca_projection.png"
POV_FILE = HERE / "submit" / "plt1_pca_pov.png"
POV_TARGET = 0.8


def show(a):
    return np.array2string(np.asarray(a), formatter={"float_kind": lambda v: f"{v:.6g}"}, max_line_width=200)

def fix_sign(V):
    rows = np.argmax(np.abs(V), axis=0)
    return V * np.sign(V[rows, np.arange(V.shape[1])])

def pca(X):
    m = X.mean(axis=0)
    D = X - m
    S = D.T @ D / len(X)
    lam, V = np.linalg.eigh(S)
    order = np.argsort(lam)[::-1]
    return m, S, lam[order], fix_sign(V[:, order])

def pov(lam):
    return np.cumsum(lam) / np.sum(lam)

def plot_projection(Z, y, path):
    plt.figure(figsize=(8, 6))
    for c in np.unique(y):
        plt.scatter(Z[y == c, 0], Z[y == c, 1], s=8, label=f"class {c}")
    plt.xlabel("z1")
    plt.ylabel("z2")
    plt.title("PCA (data1.csv)")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.grid(True)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

def plot_pov(p, k, path, title):
    dims = np.arange(1, len(p) + 1)
    plt.figure(figsize=(8, 5))
    plt.plot(dims, p, "o-")
    plt.axhline(POV_TARGET, color="r", linestyle="--", label=f"POV = {POV_TARGET}")
    plt.plot(k, p[k - 1], "r*", markersize=15, label=f"k = {k}")
    plt.xticks(dims)
    plt.ylim(0, 1.05)
    plt.xlabel("number of dimensions")
    plt.ylabel("POV")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig(path, dpi=150)
    plt.close()

def main():
    data = np.loadtxt(DATA_FILE, delimiter=",")
    X, y = data[:, :-1], data[:, -1].astype(int)
    classes = np.unique(y)
    print(f"data1.csv: N = {len(X)}, d = {X.shape[1]}, K = {len(classes)} classes {classes.tolist()}")
    print(f"rows per class: { {int(c): int(np.sum(y == c)) for c in classes} }")

    m, S, lam, V = pca(X)
    print(f"\nsample mean m =\n{show(m)}")
    print(f"trace of Sigma = {np.trace(S):.6g} (sum of all eigenvalues = {lam.sum():.6g})")
    print("\nall 20 eigenvalues of Sigma, largest first:")
    for j, v in enumerate(lam, 1):
        print(f"  lam{j} = {v:.6g}")

    print(f"\n(b) lam1 = {lam[0]:.6f},  lam2 = {lam[1]:.6f}")

    W = V[:, :2]
    print("\n(c) projection matrix W = [w1 w2] (20 x 2)")
    for j, (a, b) in enumerate(W, 1):
        print(f"  {j:2d}  {a:+.6f}  {b:+.6f}")
    print(f"W^T W =\n{show(W.T @ W)}")

    Z = (X - m) @ W
    print(f"\n(d) z = W^T (x - m); variance of z1 = {Z[:, 0].var():.6f}, variance of z2 = {Z[:, 1].var():.6f}")
    print("class means in the 2-D space:")
    for c in classes:
        print(f"  class {c}: z = ({Z[y == c, 0].mean():+.4f}, {Z[y == c, 1].mean():+.4f}),  "
            f"std = ({Z[y == c, 0].std():.4f}, {Z[y == c, 1].std():.4f})")
    plot_projection(Z, y, PLOT_FILE)
    print(f"saved {PLOT_FILE.name}")

    p = pov(lam)
    k = int(np.argmax(p >= POV_TARGET)) + 1
    print("\n(e) POV(k) = (lam1 + ... + lamk) / (lam1 + ... + lam20)")
    for j, v in enumerate(p, 1):
        print(f"  k = {j:2d}: POV = {v:.6f}")
    print(f"smallest k with POV >= {POV_TARGET}: k = {k} (POV = {p[k - 1]:.6f})")
    plot_pov(p, k, POV_FILE, "PCA proportion of variance")
    print(f"saved {POV_FILE.name}")

if __name__ == "__main__":
    main()
