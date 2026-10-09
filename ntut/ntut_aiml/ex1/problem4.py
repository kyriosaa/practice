# problem 4:

import numpy as np

TRAIN_FILE = "ex_q/regrs1_trn.csv"
TEST_FILE = "ex_q/regrs1_tst.csv"
ORDER_1 = 6
ORDER_2 = 4
RESULT_1 = "result4.csv"
RESULT_2 = "result4_1.csv"
RESULT_DIFF = "result4_2.csv"

def design(x, k):
    return np.column_stack([x ** j for j in range(k + 1)])

def fit(x, r, k):
    D = design(x, k)
    return np.linalg.solve(D.T @ D, D.T @ r)

def g(w, x):
    return design(x, len(w) - 1) @ w

def r_squared(r, predicted):
    e_rse = np.sum((r - predicted) ** 2) / np.sum((r - r.mean()) ** 2)
    return 1 - e_rse, e_rse

def polynomial(w):
    terms = [f"({wj:.6g})" + ("" if j == 0 else " x" if j == 1 else f" x^{j}") for j, wj in enumerate(w)]
    return "g(x) = " + " + ".join(terms)

def write(path, x, values):
    with open(path, "w", newline="") as f:
        for a, b in zip(x, values):
            f.write(f"{a:.10g},{b:.10g}\n")

def main():
    train_data = np.loadtxt(TRAIN_FILE, delimiter=",")
    x, r = train_data[:, 0], train_data[:, 1]
    x_test = np.loadtxt(TEST_FILE, delimiter=",")
    print(f"training data: N = {len(x)}, x from {x.min():.6g} to {x.max():.6g}, r from {r.min():.6g} to {r.max():.6g}")
    print(f"testing data: {len(x_test)} rows, x from {x_test.min():.6g} to {x_test.max():.6g}")

    results = {}
    for part, k in (("(1)-(3)", ORDER_1), ("(4)", ORDER_2)):
        w = fit(x, r, k)
        r2, e_rse = r_squared(r, g(w, x))
        results[k] = g(w, x_test)
        print(f"\n{part} polynomial of order {k}")
        for j, wj in enumerate(w):
            print(f"  w_{j} = {wj:.6g}")
        print("  " + polynomial(w))
        print(f"  on the training data: E_RSE = {e_rse:.6g},  R^2 = 1 - E_RSE = {r2:.8f}")
        print(f"  sum of squared errors = {np.sum((r - g(w, x)) ** 2):.6g},  "
            f"mean squared error = {np.mean((r - g(w, x)) ** 2):.6g}")

    g1, g2 = results[ORDER_1], results[ORDER_2]
    difference = np.abs(g1 - g2)
    write(RESULT_1, x_test, g1)
    write(RESULT_2, x_test, g2)
    write(RESULT_DIFF, x_test, difference)
    print(f"\nwrote {RESULT_1} (order {ORDER_1}), {RESULT_2} (order {ORDER_2}) "
        f"and {RESULT_DIFF} (absolute difference)")
    print(f"|g1(x) - g2(x)| on the testing data: mean = {difference.mean():.6g}, smallest = {difference.min():.6g}, "
        f"largest = {difference.max():.6g} at x = {x_test[np.argmax(difference)]:.6g}")
    print("mean |g1(x) - g2(x)| by range of x:")
    edges = np.linspace(-2, 2, 9)
    for a, b in zip(edges[:-1], edges[1:]):
        inside = (x_test >= a) & (x_test < b)
        print(f"  {a:+.1f} <= x < {b:+.1f}: {difference[inside].mean():8.3f}   ({int(inside.sum())} rows)")

if __name__ == "__main__":
    main()
