# problem 3

from pathlib import Path
import numpy as np
from scipy.linalg import eigh
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "ex_q" / "data2.csv"
PLOT_FILE = HERE / "submit" / "plt3_le_projection.png"
SIGMA = 10.0
ZERO_TOL = 1e-12


def show(a):
    return np.array2string(np.asarray(a), formatter={"float_kind": lambda v: f"{v:.6g}"}, max_line_width=200)

def distances(X):
    return np.sqrt(np.sum((X[:, None, :] - X[None, :, :]) ** 2, axis=2))

def similarity(D, sigma):
    B = np.exp(-D ** 2 / (2 * sigma ** 2))
    np.fill_diagonal(B, 0)
    return B

def laplacian_eigenmaps(B):
    d = B.sum(axis=1)
    D = np.diag(d)
    L = D - B
    lam, Z = eigh(L, D)
    return d, L, lam, Z

def symmetric_eigenvalues(B, d):
    s = 1 / np.sqrt(d)
    return np.linalg.eigvalsh(np.eye(len(B)) - s[:, None] * B * s[None, :])

def plot_projection(Z, y, path):
    plt.figure(figsize=(8, 6))
    for c in np.unique(y):
        plt.scatter(Z[y == c, 0], Z[y == c, 1], s=30, label=f"class {c}")
    plt.xlabel("z1")
    plt.ylabel("z2")
    plt.title("Laplacian Eigenmaps (data2.csv, sigma = 10)")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.grid(True)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

def main():
    data = np.loadtxt(DATA_FILE, delimiter=",")
    X, y = data[:, :-1], data[:, -1].astype(int)
    classes = np.unique(y)
    print(f"data2.csv: N = {len(X)}, d = {X.shape[1]}, K = {len(classes)} classes {classes.tolist()}")

    Dist = distances(X)
    r, s = np.triu_indices(len(X), k=1)
    print(f"\nEuclidean distances: smallest = {Dist[r, s].min():.6f}, median = {np.median(Dist[r, s]):.6f}, "
        f"largest = {Dist[r, s].max():.6f}")

    B = similarity(Dist, SIGMA)
    print(f"B_rs = exp(-d_rs^2 / (2 * {SIGMA:g}^2)) for r != s, B_rr = 0")
    print(f"similarities: smallest = {B[r, s].min():.6f}, largest = {B[r, s].max():.6f}, "
        f"pairs with B_rs > 0.5: {int(np.sum(B[r, s] > 0.5))} of {len(r)}")

    d, L, lam, Z = laplacian_eigenmaps(B)
    print(f"degrees d_r = sum_s B_rs: smallest = {d.min():.6f}, largest = {d.max():.6f}")
    print(f"L is symmetric: {np.allclose(L, L.T)}, every row of L adds up to 0: {np.allclose(L.sum(axis=1), 0)}")

    check = symmetric_eigenvalues(B, d)
    print("\n10 smallest generalized eigenvalues of L z = lam D z")
    for j in range(10):
        print(f"  {j + 1:2d}: {lam[j]:+.6e}   (from D^-1/2 L D^-1/2: {check[j]:+.6e})")
    zero = lam <= ZERO_TOL
    keep = np.where(~zero)[0][:2]
    z0 = Z[:, 0] / Z[0, 0]
    print(f"eigenvalues counted as 0 (<= {ZERO_TOL:g}): {int(zero.sum())}, "
        f"its eigenvector is constant: {np.allclose(z0, 1)}")

    l1, l2 = lam[keep]
    print(f"\n(b) smallest non-zero lam = {l1:.6f},  2nd smallest non-zero lam = {l2:.6f}")

    W = Z[:, keep]
    W = W * np.sign(W[np.argmax(np.abs(W), axis=0), [0, 1]])
    residual = np.abs(L @ W - (d[:, None] * W) * lam[keep]).max()
    print(f"check: max |L z - lam D z| = {residual:.3g},  z^T D z = {show(np.sum(d[:, None] * W ** 2, axis=0))}, "
        f"z^T D 1 = {show(d @ W)}")

    print("\n(c) W = [z1 z2] (63 x 2); row t is the 2-D position of x_t")
    print("row  class         z1          z2")
    for t in range(len(X)):
        print(f"{t + 1:3d}  {y[t]:5d}  {W[t, 0]:+.6f}  {W[t, 1]:+.6f}")

    print("\n(d) class means in the 2-D space:")
    for c in classes:
        print(f"  class {c}: z = ({W[y == c, 0].mean():+.6f}, {W[y == c, 1].mean():+.6f}),  "
            f"std = ({W[y == c, 0].std():.6f}, {W[y == c, 1].std():.6f})")
    order = [int(c) for c in classes[np.argsort([W[y == c, 0].mean() for c in classes])]]
    print(f"classes ordered by their mean z1: {order}")
    centered = W[:, 0] - W[:, 0].mean()
    print(f"correlation between z2 and (z1 - mean z1)^2 = {np.corrcoef(W[:, 1], centered ** 2)[0, 1]:.6f}")
    print(f"correlation between z1 and the mean of the 18 features of each row = "
        f"{np.corrcoef(W[:, 0], X.mean(axis=1))[0, 1]:.6f}")
    plot_projection(W, y, PLOT_FILE)
    print(f"saved {PLOT_FILE.name}")

if __name__ == "__main__":
    main()
