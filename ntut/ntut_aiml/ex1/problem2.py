# problem 2:

from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
TRAIN_FILE = "ex_q/cls2_trn.csv"
TEST_FILE ="ex_q/cls2_tst.csv"
RESULT_FILE = "result2.csv"

def show(a):
    return np.array2string(np.asarray(a), formatter={"float_kind": lambda v: f"{v:.6g}"}, max_line_width=200)

def train(X, y):
    classes = np.unique(y)
    priors, means, covs = [], [], []
    S = np.zeros((X.shape[1], X.shape[1]))
    for c in classes:
        Xc = X[y == c]
        m = Xc.mean(axis=0)
        D = Xc - m
        S_i = D.T @ D / len(Xc)
        priors.append(len(Xc) / len(X))
        means.append(m)
        covs.append(S_i)
        S += priors[-1] * S_i
    return classes, np.array(priors), np.array(means), S, np.array(covs)

def weights(priors, means, S):
    S_inv = np.linalg.inv(S)
    w = means @ S_inv
    w0 = -0.5 * np.sum(means @ S_inv * means, axis=1) + np.log(priors)
    return w, w0

def scores(X, w, w0):
    return X @ w.T + w0

def confusion(actual, predicted, classes):
    return np.array([[np.sum((actual == a) & (predicted == p)) for p in classes] for a in classes])

def main():
    train_data = np.loadtxt(TRAIN_FILE, delimiter=",")
    X, y = train_data[:, :-1], train_data[:, -1].astype(int)
    test = np.loadtxt(TEST_FILE, delimiter=",")

    classes, priors, means, S, covs = train(X, y)
    w, w0 = weights(priors, means, S)
    print(f"training data: N = {len(X)}, d = {X.shape[1]}, K = {len(classes)} classes {classes.tolist()}")
    print(f"testing data: {len(test)} rows")

    predicted_train = classes[np.argmax(scores(X, w, w0), axis=1)]
    correct = int(np.sum(predicted_train == y))
    print(f"\n(1) training accuracy = {correct}/{len(y)} = {correct / len(y):.4%}")
    print("confusion matrix on the training data (rows = actual class, columns = predicted class):")
    print(confusion(y, predicted_train, classes))

    print("\ndiscriminant functions g_i(x) = w_i^T x + w_i0")
    print("w_i = S^-1 m_i,  w_i0 = -1/2 m_i^T S^-1 m_i + log P(C_i)")
    print("(x^T S^-1 x and log|S| are the same for every class, so they are dropped)")
    for c, P, m, wi, wi0 in zip(classes, priors, means, w, w0):
        print(f"\nCLASS {c}")
        print(f"N_{c} = {int(np.sum(y == c))},  P(C_{c}) = {P:.6g}")
        print(f"m_{c} =\n{show(m)}")
        print(f"w_{c} =\n{show(wi)}")
        print(f"w_{c}0 = {wi0:.6g}")

    print(f"\n(2) covariance matrix S =\n{show(S)}")
    print(f"|S| = {np.linalg.det(S):.6e}")
    print(f"standard deviations from S: {np.sqrt(np.diag(S)).min():.3f} to {np.sqrt(np.diag(S)).max():.3f}")
    print("\nwhat every class looks like before pooling (from its own S_i):")
    print("  class   mean of m_i   standard deviations   average correlation")
    for c, m, S_i in zip(classes, means, covs):
        s = np.sqrt(np.diag(S_i))
        R = S_i / np.outer(s, s)
        average = (R.sum() - len(s)) / (len(s) * (len(s) - 1))
        print(f"  {c:5d}   {m.mean():11.3f}   {s.min():7.3f} to {s.max():6.3f}   {average:19.3f}")

    predicted = classes[np.argmax(scores(test, w, w0), axis=1)]
    with open(RESULT_FILE, "w", newline="") as f:
        for row, c in zip(test, predicted):
            f.write(",".join(f"{v:.10g}" for v in row) + f",{c}\n")
    print(f"\n(3) wrote {len(predicted)} rows to {RESULT_FILE}")
    print(f"testing rows per class: { {int(c): int(np.sum(predicted == c)) for c in classes} }")

if __name__ == "__main__":
    main()
