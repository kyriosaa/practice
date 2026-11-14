# problem 5

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "ex_q" / "clstr_data.csv"
PLOT_FILE = HERE / "submit" / "plt5_kmeans_norms.png"
K = 8
MAX_ITER = 1000
CHECK_RUNS = 100


def show(a):
    return np.array2string(np.asarray(a), formatter={"float_kind": lambda v: f"{v:.4f}"}, max_line_width=200)

def kmeans(X, C):
    C = C.copy()
    history, log = [C.copy()], []
    labels = None
    for it in range(1, MAX_ITER + 1):
        d = np.sum((X[:, None, :] - C[None, :, :]) ** 2, axis=2)
        new = np.argmin(d, axis=1)
        moved = len(X) if labels is None else int(np.sum(new != labels))
        old = C.copy()
        for k in range(K):
            if np.any(new == k):
                C[k] = X[new == k].mean(axis=0)
        labels = new
        history.append(C.copy())
        J = float(np.sum((X - C[labels]) ** 2))
        shift = float(np.max(np.linalg.norm(C - old, axis=1)))
        log.append((it, moved, np.bincount(labels, minlength=K), J, shift))
        if it > 1 and moved == 0:
            break
    return C, labels, np.array(history), log

def random_starts(X, runs, seed=0):
    rng = np.random.default_rng(seed)
    results, best = [], None
    for _ in range(runs):
        C, labels, _, log = kmeans(X, X[rng.choice(len(X), K, replace=False)])
        results.append(log[-1][3])
        if best is None or results[-1] < best[0]:
            best = (results[-1], C, labels)
    return np.array(results), best

def plot_norms(history, path):
    norms = np.linalg.norm(history, axis=2)
    plt.figure(figsize=(9, 6))
    for k in range(K):
        plt.plot(norms[:, k], "o-", markersize=3, label=f"center {k + 1}")
    plt.xlabel("iteration")
    plt.ylabel("2-norm of cluster center")
    plt.title("2-norms of the 8 cluster centers")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.grid(True)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

def main():
    X = np.loadtxt(DATA_FILE, delimiter=",")
    print(f"clstr_data.csv: N = {len(X)}, d = {X.shape[1]}, K = {K}")
    print(f"data range: {X.min():.4f} to {X.max():.4f}, data mean norm = {np.linalg.norm(X.mean(axis=0)):.4f}")

    C, labels, history, log = kmeans(X, np.zeros((K, X.shape[1])))
    print("\n(a) iterations (moved = points that changed cluster, J = sum of squared distances to the centers)")
    print(" it  moved  cluster sizes                              J              max center shift")
    for it, moved, sizes, J, shift in log:
        print(f"{it:3d}  {moved:5d}  {str(sizes.tolist()):42s} {J:14.4f}  {shift:12.6f}")
    print(f"converged after {len(log)} iterations: iteration {len(log)} moved no points and no center moved")

    print("\n(b) convergent cluster centers")
    for k in range(K):
        print(f"m{k + 1} (N = {int(np.sum(labels == k))}, |m{k + 1}| = {np.linalg.norm(C[k]):.4f}) =\n{show(C[k])}")

    norms = np.linalg.norm(history, axis=2)
    print("\n(d) 2-norms of the centers at every iteration (iteration 0 is the start)")
    print(" it  " + "  ".join(f"   |m{k + 1}|" for k in range(K)))
    for it, row in enumerate(norms):
        print(f"{it:3d}  " + "  ".join(f"{v:8.4f}" for v in row))
    first = [int(np.argmax(norms[:, k] > 0)) for k in range(K)]
    print(f"iteration at which each center first leaves the origin: {first}")
    plot_norms(history, PLOT_FILE)
    print(f"saved {PLOT_FILE.name}")

    J = log[-1][3]
    others, (best_J, best_C, best_labels) = random_starts(X, CHECK_RUNS)
    print(f"\ncheck: J from the origin start = {J:.4f}")
    print(f"{CHECK_RUNS} runs from 8 random data points: smallest J = {others.min():.4f}, median = {np.median(others):.4f}, "
        f"largest = {others.max():.4f}, runs with J below the origin start = {int(np.sum(others < J - 1e-6))}")
    print("centers sorted by the mean of their 15 coordinates (size, mean coordinate):")
    for name, C_, labels_ in (("origin start", C, labels), ("best random start", best_C, best_labels)):
        order = np.argsort(C_.mean(axis=1))
        print(f"  {name:17s} " + "  ".join(f"({int(np.sum(labels_ == k))}, {C_[k].mean():+.2f})" for k in order))

if __name__ == "__main__":
    main()
