# problem 1

from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
TRAIN_FILE = "ex_q/cls1_trn.csv"
TEST_FILE = "ex_q/cls1_tst.csv"
RESULT_FILE = "result1.csv"
CHECK_ROWS = [3, 10]

def show(a):
    return np.array2string(np.asarray(a), formatter={"float_kind": lambda v: f"{v:.6g}"}, max_line_width=200)

def train(X, y):
    classes = np.unique(y)
    priors, means, covs = [], [], []
    for c in classes:
        Xc = X[y == c]
        m = Xc.mean(axis=0)
        D = Xc - m
        priors.append(len(Xc) / len(X))
        means.append(m)
        covs.append(D.T @ D / len(Xc))
    return classes, np.array(priors), np.array(means), np.array(covs)

def discriminant(X, prior, m, S):
    D = X - m
    distance = np.sum(D @ np.linalg.inv(S) * D, axis=1)
    return -0.5 * np.linalg.slogdet(S)[1] - 0.5 * distance + np.log(prior)

def scores(X, priors, means, covs):
    return np.column_stack([discriminant(X, P, m, S) for P, m, S in zip(priors, means, covs)])

def confusion(actual, predicted, classes):
    return np.array([[np.sum((actual == a) & (predicted == p)) for p in classes] for a in classes])

def main():
    train_data = np.loadtxt(TRAIN_FILE, delimiter=",")
    X, y = train_data[:, :-1], train_data[:, -1].astype(int)
    test = np.loadtxt(TEST_FILE, delimiter=",")

    classes, priors, means, covs = train(X, y)
    print(f"training data: N = {len(X)}, d = {X.shape[1]}, K = {len(classes)} classes {classes.tolist()}")
    print(f"testing data: {len(test)} rows")

    predicted_train = classes[np.argmax(scores(X, priors, means, covs), axis=1)]
    correct = int(np.sum(predicted_train == y))
    print(f"\n(1) training accuracy = {correct}/{len(y)} = {correct / len(y):.4%}")
    print("confusion matrix on the training data (rows = actual class, columns = predicted class):")
    print(confusion(y, predicted_train, classes))

    print("\ndiscriminant functions g_i(x) = x^T W_i x + w_i^T x + w_i0")
    print("W_i = -1/2 S_i^-1,  w_i = S_i^-1 m_i,  w_i0 = -1/2 m_i^T S_i^-1 m_i - 1/2 log|S_i| + log P(C_i)")
    dets = []
    for c, P, m, S in zip(classes, priors, means, covs):
        S_inv = np.linalg.inv(S)
        W = -0.5 * S_inv
        w = S_inv @ m
        w0 = -0.5 * m @ S_inv @ m - 0.5 * np.linalg.slogdet(S)[1] + np.log(P)
        dets.append(np.linalg.det(S))
        print(f"\nCLASS {c}")
        print(f"N_{c} = {int(np.sum(y == c))},  P(C_{c}) = {P:.6g}")
        print(f"m_{c} =\n{show(m)}")
        print(f"S_{c} =\n{show(S)}")
        print(f"W_{c} =\n{show(W)}")
        print(f"w_{c} =\n{show(w)}")
        print(f"w_{c}0 = {w0:.6g}")

    print("\n(2) determinants of the covariance matrices")
    for c, det in zip(classes, dets):
        print(f"|S_{c}| = {det:.6e}")

    G = scores(test, priors, means, covs)
    predicted = classes[np.argmax(G, axis=1)]
    with open(RESULT_FILE, "w", newline="") as f:
        for row, c in zip(test, predicted):
            f.write(",".join(f"{v:.10g}" for v in row) + f",{c}\n")
    print(f"\n(3) wrote {len(predicted)} rows to {RESULT_FILE}")
    print(f"testing rows per class: { {int(c): int(np.sum(predicted == c)) for c in classes} }")

    print("\n(4) discriminant values for single testing rows")
    for n in CHECK_ROWS:
        x, g = test[n - 1], G[n - 1]
        best = classes[np.argmax(g)]
        print(f"\nx_{n} = {show(x)}")
        for c, value in zip(classes, g):
            print(f"  g_{c}(x_{n}) = {value:.6f}")
        print(f"  the largest is g_{best}(x_{n}), so x_{n} is class {best}")
        print(f"  row {n} of {RESULT_FILE} says class {predicted[n - 1]}")

if __name__ == "__main__":
    main()
