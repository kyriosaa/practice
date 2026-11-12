import os
import sys
import cv2
import numpy

# cv2 is only used for imread / imwrite / line, everything else is done by hand

TEST_DIR    = "test_img"
RESULT_DIR  = "result_img"
DEBUG_DIR   = "debug_img"       # extra pictures for the report, only made with --debug
PAD_MODE    = "edge"

# parameters per image
#   gauss_k / gauss_sigma   : gaussian kernel size and standard deviation
#   low / high              : double threshold on the sobel gradient magnitude
#   hough_thresh            : min votes for a (rho, theta) cell to count as a line
PARAMS = {
    "img1": dict(gauss_k=5, gauss_sigma=1.4, low=40, high=100, hough_thresh=90),
    "img2": dict(gauss_k=7, gauss_sigma=2.0, low=40, high=100, hough_thresh=120),
    "img3": dict(gauss_k=5, gauss_sigma=1.4, low=50, high=130, hough_thresh=90),
}

# hough settings (same for every image)
THETA_STEP      = 1.0   # degrees
RHO_STEP        = 1.0   # pixels
MAX_LINES       = 20    # only keep the 20 strongest lines after peak suppression
PEAK_THETA_WIN  = 5     # a peak suppresses other peaks within +-5 deg ...
PEAK_RHO_WIN    = 8     # ... and +-8 px (img3's inner/outer border are only ~13 px apart)

# corner search settings
PARALLEL_TOL    = 15    # two lines are "parallel" if their directions differ by < 15 deg
PERP_TOL        = 30    # two pairs are "perpendicular" if they differ by 90 +- 30 deg
MIN_SIDE_FRAC   = 0.15  # each side of the quad must be at least 15% of the image's short side
SUPPORT_TOL     = 1     # an edge pixel within 1 px of a side counts as support
MIN_SUPPORT     = 0.6   # every side needs >= 60% of its length covered by edge pixels


# ---------------------------------------------------------------- Q1
def grayify(img):
    # same formula as hw1 (ITU-R BT.601), cv2 gives B, G, R order
    b = img[:, :, 0].astype(numpy.float64)
    g = img[:, :, 1].astype(numpy.float64)
    r = img[:, :, 2].astype(numpy.float64)

    return 0.299*r + 0.587*g + 0.114*b

def gaussian_kernel(k, sigma):
    ax = numpy.arange(k) - k // 2
    xx, yy = numpy.meshgrid(ax, ax)
    kernel = (1 / (2 * numpy.pi * sigma**2)) * numpy.exp(-(xx**2 + yy**2) / (2 * sigma**2))

    # the raw formula only sums to ~1 for big kernels, so normalise it or the image gets darker
    return kernel / kernel.sum()

def pad(img, p):
    return numpy.pad(img, p, mode=PAD_MODE)

def conv(img, kernel):
    # same shift-and-add idea as hw2: for each kernel cell, shift the whole image and add it in
    # stride 1, padding k//2 so the output is the same size as the input
    # (no kernel flip, so technically cross-correlation, same as cv2.filter2D)
    kh, kw = kernel.shape
    padded = pad(img.astype(numpy.float64), ((kh // 2, kh // 2), (kw // 2, kw // 2)))
    h, w = img.shape
    out = numpy.zeros((h, w))

    for m in range(kh):
        for n in range(kw):
            out += padded[m : m + h, n : n + w] * kernel[m, n]

    return out      # float, no rounding/clipping here

def gaussian_blur(gray, k, sigma):
    return conv(gray, gaussian_kernel(k, sigma))

def to_uint8(img):
    return numpy.clip(numpy.round(img), 0, 255).astype(numpy.uint8)


# ---------------------------------------------------------------- Q2
SOBEL_X = numpy.array([[-1, 0, 1],
                       [-2, 0, 2],
                       [-1, 0, 1]], dtype=numpy.float64)
SOBEL_Y = numpy.array([[-1, -2, -1],
                       [ 0,  0,  0],
                       [ 1,  2,  1]], dtype=numpy.float64)

def sobel_gradient(img):
    gx = conv(img, SOBEL_X)
    gy = conv(img, SOBEL_Y)

    magnitude = numpy.sqrt(gx**2 + gy**2)

    # image rows go DOWN, so flip gy to get a normal maths angle (counter-clockwise, y up).
    # that way 45 deg really points to the top-right like on the slides.
    # arctan2 instead of arctan(gy/gx) so gx = 0 doesnt divide by zero
    angle = numpy.degrees(numpy.arctan2(-gy, gx))       # -180 .. 180

    return gx, gy, magnitude, angle

def quantize_angle(angle):
    # an edge direction and its opposite are the same thing for nms, so fold into 0..180
    a = numpy.mod(angle, 180)
    q = numpy.zeros(a.shape, dtype=numpy.int32)    # 0 deg:  [0, 22.5) and [157.5, 180)
    q[(a >= 22.5) & (a < 67.5)]  = 45
    q[(a >= 67.5) & (a < 112.5)] = 90
    q[(a >= 112.5) & (a < 157.5)] = 135

    return q

def non_max_suppression(mag, angle):
    h, w = mag.shape
    q = quantize_angle(angle)
    p = numpy.pad(mag, 1, mode="constant")     # zero border so the edges of the image work too

    # neighbours of every pixel, p[1:-1, 1:-1] is the pixel itself
    left        = p[1:-1, :-2]
    right       = p[1:-1, 2:]
    up          = p[:-2, 1:-1]
    down        = p[2:, 1:-1]
    up_right    = p[:-2, 2:]
    down_left   = p[2:, :-2]
    up_left     = p[:-2, :-2]
    down_right  = p[2:, 2:]

    # the two neighbours along the gradient direction for each of the 4 bins
    n1 = numpy.zeros((h, w))
    n2 = numpy.zeros((h, w))
    for d, a, b in [(0, left, right), (45, up_right, down_left),
                    (90, up, down), (135, up_left, down_right)]:
        sel = (q == d)
        n1[sel] = a[sel]
        n2[sel] = b[sel]

    keep = (mag >= n1) & (mag >= n2)
    return numpy.where(keep, mag, 0.0)

def double_threshold(nms, low, high):
    strong = nms >= high
    weak = (nms >= low) & (nms < high)

    return strong, weak

def hysteresis(strong, weak):
    h, w = strong.shape
    edges = strong.copy()
    stack = list(zip(*numpy.nonzero(strong)))

    # flood out from every strong pixel, any weak pixel touching it (8-neighbourhood) gets
    # promoted to strong and then gets to spread too. weak pixels never reached are dropped.
    while stack:
        r, c = stack.pop()
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                rr, cc = r + dr, c + dc
                if 0 <= rr < h and 0 <= cc < w and weak[rr, cc] and not edges[rr, cc]:
                    edges[rr, cc] = True
                    stack.append((rr, cc))

    return edges

def canny(blurred, low, high):
    gx, gy, mag, angle = sobel_gradient(blurred)
    nms = non_max_suppression(mag, angle)
    strong, weak = double_threshold(nms, low, high)
    edges = hysteresis(strong, weak)

    steps = dict(gx=gx, gy=gy, mag=mag, angle=angle, nms=nms, strong=strong, weak=weak)
    return edges, steps


# ---------------------------------------------------------------- Q3
def hough_transform(edges, theta_step=THETA_STEP, rho_step=RHO_STEP):
    h, w = edges.shape
    diag = numpy.sqrt(h**2 + w**2)

    thetas = numpy.arange(0, 360, theta_step)                   # 0 .. 360 deg
    rhos = numpy.arange(0, diag + rho_step, rho_step)           # 0 .. diagonal
    acc = numpy.zeros((len(rhos), len(thetas)), dtype=numpy.int64)

    ys, xs = numpy.nonzero(edges)                               # x = column, y = row

    # every edge pixel votes once per theta. using all 360 deg with rho >= 0 means each line
    # has exactly one (rho, theta), the negative-rho half is the same line at theta + 180
    for t, theta in enumerate(numpy.radians(thetas)):
        rho = xs * numpy.cos(theta) + ys * numpy.sin(theta)
        idx = numpy.round(rho / rho_step).astype(numpy.int64)   # closest rho bin
        idx = idx[(idx >= 0) & (idx < len(rhos))]
        acc[:, t] += numpy.bincount(idx, minlength=len(rhos))

    return acc, rhos, thetas

def hough_peaks(acc, rhos, thetas, threshold, max_lines):
    # walk the cells from most votes to least, a cell is a line if it beats the threshold
    # and isnt right next to a line we already took (otherwise one edge gives 10 lines)
    n_t = len(thetas)
    order = numpy.argsort(acc, axis=None)[::-1]
    lines = []

    for flat in order:
        votes = acc.flat[flat]
        if votes < threshold or len(lines) >= max_lines:
            break
        r, t = divmod(int(flat), n_t)

        too_close = False
        for (_, _, r2, t2) in lines:
            dt = abs(t - t2)
            dt = min(dt, n_t - dt)      # theta wraps around at 360
            if dt * THETA_STEP <= PEAK_THETA_WIN and abs(r - r2) * RHO_STEP <= PEAK_RHO_WIN:
                too_close = True
                break
        if not too_close:
            lines.append((rhos[r], thetas[t], r, t))

    return [(rho, theta, int(acc[r, t])) for rho, theta, r, t in lines]

def intersect(l1, l2):
    # solve  x cos t1 + y sin t1 = r1
    #        x cos t2 + y sin t2 = r2
    r1, t1 = l1[0], numpy.radians(l1[1])
    r2, t2 = l2[0], numpy.radians(l2[1])
    det = numpy.cos(t1) * numpy.sin(t2) - numpy.sin(t1) * numpy.cos(t2)
    if abs(det) < 1e-6:
        return None     # parallel
    x = (r1 * numpy.sin(t2) - r2 * numpy.sin(t1)) / det
    y = (r2 * numpy.cos(t1) - r1 * numpy.cos(t2)) / det

    return x, y

def direction_diff(t1, t2):
    # angle between two lines ignoring which way they point, 0 .. 90
    d = abs(t1 - t2) % 180
    return min(d, 180 - d)

def side_support(near_edge, p1, p2):
    # walk along the segment p1 -> p2 one pixel at a time and count how much of it sits on an edge
    h, w = near_edge.shape
    n = int(max(abs(p2[0] - p1[0]), abs(p2[1] - p1[1]))) + 1
    xs = numpy.round(numpy.linspace(p1[0], p2[0], n)).astype(int)
    ys = numpy.round(numpy.linspace(p1[1], p2[1], n)).astype(int)
    inside = (xs >= 0) & (xs < w) & (ys >= 0) & (ys < h)
    if inside.sum() == 0:
        return 0.0

    return near_edge[ys[inside], xs[inside]].sum() / n

def grow(edges, r):
    # binary dilation with a (2r+1)x(2r+1) square, done with shifts, so "near an edge" is cheap to check
    h, w = edges.shape
    p = numpy.pad(edges, r, mode="constant")
    out = numpy.zeros((h, w), dtype=bool)
    for dy in range(2*r + 1):
        for dx in range(2*r + 1):
            out |= p[dy : dy + h, dx : dx + w]

    return out

def order_corners(pts):
    # sort the 4 points around their centre so drawing them in order makes a quad, not a bow-tie
    cx = sum(p[0] for p in pts) / 4
    cy = sum(p[1] for p in pts) / 4
    return sorted(pts, key=lambda p: numpy.arctan2(p[1] - cy, p[0] - cx))

def quad_area(pts):
    # shoelace formula
    area = 0
    for i in range(4):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % 4]
        area += x1 * y2 - x2 * y1

    return abs(area) / 2

def find_card(lines, edges):
    h, w = edges.shape
    near_edge = grow(edges, SUPPORT_TOL)
    min_side = MIN_SIDE_FRAC * min(h, w)

    # 1) pairs of roughly parallel lines (opposite sides of the card)
    pairs = []
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            if direction_diff(lines[i][1], lines[j][1]) < PARALLEL_TOL:
                pairs.append((i, j))

    # 2) two pairs that are roughly perpendicular -> 4 corners
    best, best_score = None, -1
    for a in range(len(pairs)):
        for b in range(a + 1, len(pairs)):
            i, j = pairs[a]
            k, l = pairs[b]
            if len({i, j, k, l}) < 4:
                continue
            if abs(direction_diff(lines[i][1], lines[k][1]) - 90) > PERP_TOL:
                continue

            # sides go i -> k -> j -> l -> back to i
            corners = [intersect(lines[i], lines[k]), intersect(lines[k], lines[j]),
                       intersect(lines[j], lines[l]), intersect(lines[l], lines[i])]
            if any(c is None for c in corners):
                continue

            # every corner has to be inside the image (a few pixels of slack)
            if not all(-5 <= x < w + 5 and -5 <= y < h + 5 for x, y in corners):
                continue

            # no tiny/skinny quads
            sides = [numpy.hypot(corners[s][0] - corners[(s+1) % 4][0],
                                 corners[s][1] - corners[(s+1) % 4][1]) for s in range(4)]
            if min(sides) < min_side:
                continue

            # every side must actually lie on edge pixels, not just be an infinite hough line
            support = [side_support(near_edge, corners[s], corners[(s+1) % 4]) for s in range(4)]
            if min(support) < MIN_SUPPORT:
                continue

            # card = biggest well-supported quad (inner frames/pictures are smaller rectangles).
            # support is squared so a slightly bigger quad that sits a few px off the real
            # edge (e.g. on a wood grain line next to it) cant win just because of area
            score = quad_area(corners) * numpy.mean(support)**2
            if score > best_score:
                best_score = score
                best = dict(corners=order_corners(corners), lines=[i, j, k, l], support=support)

    return best

def draw_lines_debug(img, lines):
    # every hough line drawn across the whole image (blue), like the slide's middle picture
    out = img.copy()
    h, w = img.shape[:2]
    L = int(numpy.hypot(h, w))
    for rho, theta, _ in lines:
        t = numpy.radians(theta)
        x0, y0 = rho * numpy.cos(t), rho * numpy.sin(t)
        dx, dy = -numpy.sin(t), numpy.cos(t)
        p1 = (int(round(x0 - L*dx)), int(round(y0 - L*dy)))
        p2 = (int(round(x0 + L*dx)), int(round(y0 + L*dy)))
        cv2.line(out, p1, p2, (255, 0, 0), 1, cv2.LINE_AA)

    return out

def draw_card(img, corners):
    out = img.copy()
    pts = [(int(round(x)), int(round(y))) for x, y in corners]
    for s in range(4):
        cv2.line(out, pts[s], pts[(s + 1) % 4], (0, 255, 0), 3, cv2.LINE_AA)

    return out


# ---------------------------------------------------------------- main
def normalise_for_view(a):
    a = numpy.abs(a)
    return to_uint8(a / a.max() * 255) if a.max() > 0 else to_uint8(a)

def run(name, debug=False):
    p = PARAMS[name]
    img = cv2.imread(os.path.join(TEST_DIR, name + ".png"))

    # Q1: grayscale + gaussian blur
    gray = grayify(img)
    blurred = gaussian_blur(gray, p["gauss_k"], p["gauss_sigma"])
    cv2.imwrite(os.path.join(RESULT_DIR, name + "_q1.png"), to_uint8(blurred))

    # Q2: canny
    edges, steps = canny(blurred, p["low"], p["high"])
    cv2.imwrite(os.path.join(RESULT_DIR, name + "_q2.png"), edges.astype(numpy.uint8) * 255)

    # Q3: hough + find the 4 corners + draw
    acc, rhos, thetas = hough_transform(edges)
    lines = hough_peaks(acc, rhos, thetas, p["hough_thresh"], MAX_LINES)
    card = find_card(lines, edges)

    if card is None:
        print(f"{name}: no card found, drawing all hough lines instead")
        result = draw_lines_debug(img, lines)
    else:
        result = draw_card(img, card["corners"])
    cv2.imwrite(os.path.join(RESULT_DIR, name + "_q3.png"), result)

    print(f"{name}: {int(edges.sum())} edge px, {len(lines)} hough lines, max votes {acc.max()}")
    for n, (rho, theta, votes) in enumerate(lines):
        used = "*" if card is not None and n in card["lines"] else " "
        print(f"   {used} line {n:2d}: rho={rho:6.1f}  theta={theta:5.1f}  votes={votes}")
    if card is not None:
        print("   corners:", ", ".join(f"({x:.1f}, {y:.1f})" for x, y in card["corners"]))
        print("   side support:", ", ".join(f"{s:.2f}" for s in card["support"]))

    if debug:
        os.makedirs(DEBUG_DIR, exist_ok=True)
        cv2.imwrite(os.path.join(DEBUG_DIR, name + "_gx.png"), normalise_for_view(steps["gx"]))
        cv2.imwrite(os.path.join(DEBUG_DIR, name + "_gy.png"), normalise_for_view(steps["gy"]))
        cv2.imwrite(os.path.join(DEBUG_DIR, name + "_mag.png"), normalise_for_view(steps["mag"]))
        cv2.imwrite(os.path.join(DEBUG_DIR, name + "_angle.png"),
                    to_uint8((steps["angle"] + 180) / 360 * 255))
        cv2.imwrite(os.path.join(DEBUG_DIR, name + "_nms.png"), normalise_for_view(steps["nms"]))
        dt = numpy.zeros(edges.shape, dtype=numpy.uint8)
        dt[steps["weak"]] = 100
        dt[steps["strong"]] = 255
        cv2.imwrite(os.path.join(DEBUG_DIR, name + "_threshold.png"), dt)
        cv2.imwrite(os.path.join(DEBUG_DIR, name + "_accumulator.png"), normalise_for_view(acc))
        cv2.imwrite(os.path.join(DEBUG_DIR, name + "_hough_lines.png"), draw_lines_debug(img, lines))

if __name__ == "__main__":
    # run from anywhere, paths are relative to this file
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(RESULT_DIR, exist_ok=True)
    debug = "--debug" in sys.argv

    for name in ["img1", "img2", "img3"]:
        run(name, debug)
