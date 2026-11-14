# problem 4

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "ex_q" / "data2.csv"
PLOT_FILE = HERE / "submit" / "plt4_mds_projection.png"


def show(a):
    return np.array2string(np.asarray(a), formatter={"float_kind": lambda v: f"{v:.6g}"}, max_line_width=200)

def fix_sign(V):
    rows = np.argmax(np.abs(V), axis=0)
    return V * np.sign(V[rows, np.arange(V.shape[1])])

def distances(Z):
    return np.sqrt(np.sum((Z[:, None, :] - Z[None, :, :]) ** 2, axis=2))

def double_center(D):
    D2 = D ** 2
    return -0.5 * (D2 - D2.mean(axis=1, keepdims=True) - D2.mean(axis=0, keepdims=True) + D2.mean())

def mds(B, k):
    lam, C = np.linalg.eigh(B)
    order = np.argsort(lam)[::-1]
    lam, C = lam[order], fix_sign(C[:, order])
    return lam, C, C[:, :k] * np.sqrt(lam[:k])

def extremes(D, y):
    r, s = np.triu_indices(len(D), k=1)
    d = D[r, s]
    hi, lo = np.argmax(d), np.argmin(d)
    return [(d[i], r[i], s[i]) for i in (hi, lo)]

def plot_projection(Z, y, path):
    plt.figure(figsize=(8, 6))
    for c in np.unique(y):
        plt.scatter(Z[y == c, 0], Z[y == c, 1], s=30, label=f"class {c}")
    plt.xlabel("z1")
    plt.ylabel("z2")
    plt.title("MDS (data2.csv)")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.grid(True)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

def main():
    data = np.loadtxt(DATA_FILE, delimiter=",")
    X, y = data[:, :-1], data[:, -1].astype(int)
    classes = np.unique(y)
    print(f"data2.csv: N = {len(X)}, d = {X.shape[1]}, K = {len(classes)} classes {classes.tolist()}")
    print(f"rows per class: { {int(c): int(np.sum(y == c)) for c in classes} }")

    D = distances(X)
    B = double_center(D)
    Y = X - X.mean(axis=0)
    print(f"\nB from the distances only, Y Y^T from the centered data: max |B - Y Y^T| = {np.abs(B - Y @ Y.T).max():.3g}")

    lam, C, Z = mds(B, 2)
    print(f"\neigenvalues of Y Y^T (63 x 63), largest first:")
    print(show(lam[:20]))
    print(f"eigenvalues 19 to 63 are 0 within rounding, largest |lam| among them = {np.abs(lam[18:]).max():.3g}")
    print(f"\n(b) lam1 = {lam[0]:.6f},  lam2 = {lam[1]:.6f}")
    print(f"(lam1 + lam2) / sum of all eigenvalues = {(lam[0] + lam[1]) / lam[lam > 0].sum():.6f}")

    print("\n(c) z = [sqrt(lam1) c1, sqrt(lam2) c2], c1 and c2 are unit eigenvectors of Y Y^T")
    print("row  class        c1          c2          z1          z2")
    for t in range(len(X)):
        print(f"{t + 1:3d}  {y[t]:5d}  {C[t, 0]:+.6f}  {C[t, 1]:+.6f}  {Z[t, 0]:+.6f}  {Z[t, 1]:+.6f}")
    print(f"variance of z1 = {Z[:, 0].var():.6f} = lam1 / N = {lam[0] / len(X):.6f}")
    print("class means in the 2-D space:")
    for c in classes:
        print(f"  class {c}: z = ({Z[y == c, 0].mean():+.4f}, {Z[y == c, 1].mean():+.4f}),  "
            f"std = ({Z[y == c, 0].std():.4f}, {Z[y == c, 1].std():.4f})")
    plot_projection(Z, y, PLOT_FILE)
    print(f"saved {PLOT_FILE.name}")

    D2 = distances(Z)
    print("\n(d) distances between all 63 * 62 / 2 = 1953 pairs of vectors")
    for name, here, other, other_name in (("18-D", D, D2, "2-D"), ("2-D", D2, D, "18-D")):
        (d_max, a, b), (d_min, e, f) = extremes(here, y)
        print(f"  {name} space: maximum = {d_max:.6f} between x{a + 1} (class {y[a]}) and x{b + 1} (class {y[b]}), "
            f"same pair in {other_name} = {other[a, b]:.6f}")
        print(f"  {name} space: minimum = {d_min:.6f} between x{e + 1} (class {y[e]}) and x{f + 1} (class {y[f]}), "
            f"same pair in {other_name} = {other[e, f]:.6f}")
    r, s = np.triu_indices(len(X), k=1)
    print(f"  every pair: 2-D distance <= 18-D distance? {bool(np.all(D2[r, s] <= D[r, s] + 1e-12))}")
    print(f"  correlation between the 1953 distances in the two spaces = {np.corrcoef(D[r, s], D2[r, s])[0, 1]:.6f}")

if __name__ == "__main__":
    main()
