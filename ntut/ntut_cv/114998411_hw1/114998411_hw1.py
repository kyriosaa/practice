import cv2
import numpy as np

# Q1
def grayify(img):
    RED     = img[:, :, 2].astype(np.float64)
    GREEN   = img[:, :, 1].astype(np.float64)
    BLUE    = img[:, :, 0].astype(np.float64)

    # google says grayscale is this formula
    GRAYSCALE = 0.299*RED + 0.587*GREEN + 0.114*BLUE
    GRAYFINAL = np.round(GRAYSCALE).astype(np.uint8)
    return GRAYFINAL

# Q2
def quantize(grayimg):
    h, w = grayimg.shape
    out = np.zeros((h, w), dtype=np.uint8)

    for i in range(h):
        for j in range(w):
            p = grayimg[i, j]   # pixel's brightness 0-255

            if p <= 63:
                out[i, j] = 0
            elif 64 <= p <= 127:
                out[i, j] = 96
            elif 128 <= p <= 191:
                out[i, j] = 160
            elif 192 <= p <= 255:
                out[i, j] = 255

    return out

def pad(img, p):
    h, w = img.shape
    padded = np.zeros((h + 2*p, w + 2*p))

    for i in range(h):
        for j in range(w):
            padded[i+p, j+p] = img[i, j]

    return padded

# Q3 & Q4
def conv(img, kernel, stride=1, padding=0):
    kh, kw = kernel.shape
    padded = pad(img, padding)
    ph, pw = padded.shape

    # output size is N+2*P - K // stride + 1
    out_h = (ph - kh) // stride + 1
    out_w = (pw - kw) // stride + 1
    out = np.zeros((out_h, out_w))

    for i in range(out_h):
        for j in range(out_w):
            r = i * stride
            c = j * stride

            total = 0
            for m in range(kh):
                for n in range(kw):
                    total += padded[r+m, c+n] * kernel[m, n]

            out[i, j] = total

    return np.round(out).astype(np.uint8)

if __name__ == "__main__":
    img = cv2.imread("test_img/taipei101.png")

    # Q1 output
    Q1img = grayify(img)
    cv2.imwrite("result_img/taipei101_Q1.png", Q1img)

    # Q2 output
    Q2img = quantize(Q1img)
    cv2.imwrite("result_img/taipei101_Q2.png", Q2img)

    # Q3 output
    box = np.ones((3, 3)) / 9   # 3x3 array
    Q3img = conv(Q1img, box, stride=1, padding=1)
    cv2.imwrite("result_img/taipei101_Q3.png", Q3img)

    # Q4 output
    down = np.array([[0, 0, 0],
                     [0, 1, 0],
                     [0, 0, 0]])
    Q4aimg = conv(Q1img, down, stride=3)
    cv2.imwrite("result_img/taipei101_Q4a.png", Q4aimg)
    Q4bimg = conv(Q3img, down, stride=3)
    cv2.imwrite("result_img/taipei101_Q4b.png", Q4bimg)