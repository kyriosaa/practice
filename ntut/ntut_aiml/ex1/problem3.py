# problem 3:

import numpy as np

TRAIN_FILE = "ex_q/cls1_trn.csv"
TEST_FILE = "ex_q/cls1_tst.csv"
RESULT_FILE = "result3.csv"
RESULT1_FILE = "result1.csv"

def show(a):
    return np.array2string(np.asarray(a), formatter={"float_kind": lambda v: f"{v:.6g}"}, max_line_width=200)

def train(X, y):
    classes = np.unique(y)
    priors, means, covs = [], [], []
    variances = np.zeros(X.shape[1])
    for c in classes:
        Xc = X[y == c]
        m = Xc.mean(axis=0)
        D = Xc - m
        priors.append(len(Xc) / len(X))
        means.append(m)
        covs.append(D.T @ D / len(Xc))
        variances += priors[-1] * np.mean(D ** 2, axis=0)
    return classes, np.array(priors), np.array(means), variances, np.array(covs)

def scores(X, priors, means, variances):
    G = []
    for P, m in zip(priors, means):
        G.append(-0.5 * np.sum((X - m) ** 2 / variances, axis=1) + np.log(P))
    return np.column_stack(G)

def gaussian_scores(X, priors, means, covs):
    G = []
    for P, m, S in zip(priors, means, covs):
        D = X - m
        distance = np.sum(D @ np.linalg.inv(S) * D, axis=1)
        G.append(-0.5 * np.linalg.slogdet(S)[1] - 0.5 * distance + np.log(P))
    return np.column_stack(G)

def confusion(actual, predicted, classes):
    return np.array([[np.sum((actual == a) & (predicted == p)) for p in classes] for a in classes])

def main():
    train_data = np.loadtxt(TRAIN_FILE, delimiter=",")
    X, y = train_data[:, :-1], train_data[:, -1].astype(int)
    test = np.loadtxt(TEST_FILE, delimiter=",")

    classes, priors, means, variances, covs = train(X, y)
    print(f"training data: N = {len(X)}, d = {X.shape[1]}, K = {len(classes)} classes {classes.tolist()}")
    print(f"testing data: {len(test)} rows")

    predicted_train = classes[np.argmax(scores(X, priors, means, variances), axis=1)]
    correct = int(np.sum(predicted_train == y))
    print(f"\n(1) training accuracy = {correct}/{len(y)} = {correct / len(y):.4%}")
    print("confusion matrix on the training data (rows = actual class, columns = predicted class):")
    print(confusion(y, predicted_train, classes))

    print("\ndiscriminant functions g_i(x) = -1/2 sum_j ((x_j - m_ij) / s_j)^2 + log P(C_i)")
    print("as a linear function: g_i(x) = w_i^T x + w_i0,  w_ij = m_ij / s_j^2,")
    print("w_i0 = -1/2 sum_j (m_ij / s_j)^2 + log P(C_i)")
    print("(sum_j (x_j / s_j)^2 is the same for every class, so it is dropped in the linear form)")
    for c, P, m in zip(classes, priors, means):
        print(f"\nCLASSS {c}")
        print(f"N_{c} = {int(np.sum(y == c))},  P(C_{c}) = {P:.6g}")
        print(f"m_{c} =\n{show(m)}")
        print(f"w_{c} =\n{show(m / variances)}")
        print(f"w_{c}0 = {-0.5 * np.sum(m ** 2 / variances) + np.log(P):.6g}")

    print(f"\n(2) variances s_j^2 on the diagonal of S =\n{show(variances)}")
    print(f"standard deviations s_j =\n{show(np.sqrt(variances))}")
    print(f"S =\n{show(np.diag(variances))}")
    print(f"|S| = {np.prod(variances):.6e}")

    predicted = classes[np.argmax(scores(test, priors, means, variances), axis=1)]
    with open(RESULT_FILE, "w", newline="") as f:
        for row, c in zip(test, predicted):
            f.write(",".join(f"{v:.10g}" for v in row) + f",{c}\n")
    print(f"\n(3) wrote {len(predicted)} rows to {RESULT_FILE}")
    print(f"testing rows per class: { {int(c): int(np.sum(predicted == c)) for c in classes} }")

    result1 = np.loadtxt(RESULT1_FILE, delimiter=",")[:, -1].astype(int)
    different = np.flatnonzero(result1 != predicted)
    print(f"\n(4) {len(different)} of {len(predicted)} testing rows have a different class "
        f"in {RESULT1_FILE} and {RESULT_FILE}")
    print("how the classes moved (problem 1 class -> problem 3 class: number of rows)")
    for a, b in sorted(set(zip(result1[different].tolist(), predicted[different].tolist()))):
        print(f"  {a} -> {b}: {int(np.sum((result1 == a) & (predicted == b)))}")
    print(f"rows that differ (counted from 1): {(different + 1).tolist()}")

    n = different[0] + 1
    print(f"\nexample, testing row {n}: problem 1 says class {result1[n - 1]}, "
        f"problem 3 says class {predicted[n - 1]}")
    print(f"x_{n} = {show(test[n - 1])}")
    for c, value in zip(classes, scores(test[n - 1:n], priors, means, variances)[0]):
        print(f"  g_{c}(x_{n}) = {value:.6f}")

    print("\nwhat every class really looks like in the training data (from the S_i of problem 1):")
    print("  class   mean of m_i   standard deviations   average correlation")
    for c, m, S in zip(classes, means, covs):
        s = np.sqrt(np.diag(S))
        R = S / np.outer(s, s)
        average = (R.sum() - len(s)) / (len(s) * (len(s) - 1))
        print(f"  {c:5d}   {m.mean():11.3f}   {s.min():7.3f} to {s.max():6.3f}   {average:19.3f}")
    print(f"problem 3 gives every class the same standard deviations, {np.sqrt(variances).min():.3f} "
        f"to {np.sqrt(variances).max():.3f}, and no correlation")

    common = np.sum(priors[:, None, None] * covs, axis=0)
    own_diagonal = np.array([np.diag(np.diag(S)) for S in covs])
    print("\ntesting rows that differ from result1.csv when only one assumption is added:")
    for name, model in (("different S_i for every class, but diagonal", own_diagonal),
                        ("common S for every class, but not diagonal", np.array([common] * len(classes)))):
        other = classes[np.argmax(gaussian_scores(test, priors, means, model), axis=1)]
        print(f"  {name}: {int(np.sum(other != result1))}")
    print(f"  common S and diagonal (problem 3): {len(different)}")

if __name__ == "__main__":
    main()
