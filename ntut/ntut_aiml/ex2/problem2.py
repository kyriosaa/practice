# problem 2

from pathlib import Path
import numpy as np
from scipy.linalg import eigh
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "ex_q" / "data1.csv"
PLOT_FILE = HERE / "submit" / "plt2_lda_projection.png"
POV_FILE = HERE / "submit" / "plt2_lda_pov.png"
POV_TARGET = 0.8


def show(a):
    return np.array2string(np.asarray(a), formatter={"float_kind": lambda v: f"{v:.6g}"}, max_line_width=200)

def fix_sign(V):
    rows = np.argmax(np.abs(V), axis=0)
    return V * np.sign(V[rows, np.arange(V.shape[1])])

def scatter_matrices(X, y):
    m = X.mean(axis=0)
    d = X.shape[1]
    S_W, S_B = np.zeros((d, d)), np.zeros((d, d))
    for c in np.unique(y):
        Xc = X[y == c]
        mc = Xc.mean(axis=0)
        D = Xc - mc
        S_W += D.T @ D
        S_B += len(Xc) * np.outer(mc - m, mc - m)
    return S_W, S_B

def lda(S_W, S_B):
    lam, V = eigh(S_B, S_W)
    order = np.argsort(lam)[::-1]
    V = V[:, order] / np.linalg.norm(V[:, order], axis=0)
    return lam[order], fix_sign(V)

def plot_projection(Z, y, path):
    plt.figure(figsize=(8, 6))
    for c in np.unique(y):
        plt.scatter(Z[y == c, 0], Z[y == c, 1], s=8, label=f"class {c}")
    plt.xlabel("z1")
    plt.ylabel("z2")
    plt.title("LDA (data1.csv)")
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

    S_W, S_B = scatter_matrices(X, y)
    print(f"rank of S_W = {np.linalg.matrix_rank(S_W)}, rank of S_B = {np.linalg.matrix_rank(S_B)} (at most K - 1 = {len(classes) - 1})")
    print(f"condition number of S_W = {np.linalg.cond(S_W):.6g}")

    lam, V = lda(S_W, S_B)
    A = np.linalg.inv(S_W) @ S_B
    print("\nall 20 eigenvalues of S_W^-1 S_B, largest first:")
    for j, v in enumerate(lam, 1):
        print(f"  lam{j} = {v:.6g}")

    print(f"\n(b) lam1 = {lam[0]:.6f},  lam2 = {lam[1]:.6f}")

    W = V[:, :2]
    print("\n(c) projection matrix W = [w1 w2] (20 x 2), every column scaled to unit length")
    for j, (a, b) in enumerate(W, 1):
        print(f"  {j:2d}  {a:+.6f}  {b:+.6f}")
    residual = np.abs(A @ W - W * lam[:2]).max()
    print(f"check: max |S_W^-1 S_B w - lam w| = {residual:.3g}")
    print(f"w1 . w2 = {W[:, 0] @ W[:, 1]:.6f} (not 0, because S_W^-1 S_B is not symmetric)")

    Z = X @ W
    print("\n(d) z = W^T x; class means in the 2-D space:")
    for c in classes:
        print(f"  class {c}: z = ({Z[y == c, 0].mean():+.4f}, {Z[y == c, 1].mean():+.4f}),  "
            f"std = ({Z[y == c, 0].std():.4f}, {Z[y == c, 1].std():.4f})")
    plot_projection(Z, y, PLOT_FILE)
    print(f"saved {PLOT_FILE.name}")

    p = np.cumsum(lam) / np.sum(lam)
    k = int(np.argmax(p >= POV_TARGET)) + 1
    print("\n(e) POV(k) = (lam1 + ... + lamk) / (lam1 + ... + lam20)")
    for j, v in enumerate(p, 1):
        print(f"  k = {j:2d}: POV = {v:.6f}")
    print(f"smallest k with POV >= {POV_TARGET}: k = {k} (POV = {p[k - 1]:.6f})")
    plot_pov(p, k, POV_FILE, "LDA proportion of variance")
    print(f"saved {POV_FILE.name}")

if __name__ == "__main__":
    main()
