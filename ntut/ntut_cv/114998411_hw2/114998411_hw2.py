import cv2
import numpy
import matplotlib.pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view

PAD_MODE = "edge"

# Q1 median filter
Q1_KERNEL   = 3
Q1_STRIDE   = 1
Q1_PADDING  = 1

# Q2 gaussian filter
Q2_KERNEL   = 7
Q2_SIGMA    = 1.0
Q2_STRIDE   = 1
Q2_PADDING  = 3

# Q3 median & gaussian
Q3_MEDIAN_KERNEL    = 3
Q3_MEDIAN_STRIDE    = 1
Q3_MEDIAN_PADDING   = 1
Q3_GAUSS_KERNEL     = 3
Q3_GAUSS_SIGMA      = 0.5
Q3_GAUSS_STRIDE     = 1
Q3_GAUSS_PADDING    = 1

def pad(img, padding):
    return numpy.pad(img, padding, mode=PAD_MODE)

# Q1
def median_filter(img, k, stride=1, padding=0):
    padded = pad(img, padding)
    windows = sliding_window_view(padded, (k, k))[::stride, ::stride]
    out = numpy.median(windows, axis=(2, 3))

    return numpy.round(out).astype(numpy.uint8)

# Q2
def gaussian_kernel(k, sigma):
    ax = numpy.arange(k) - k // 2
    xx, yy = numpy.meshgrid(ax, ax)
    kernel = numpy.exp(-(xx**2 + yy**2) / (2 * sigma**2))

    return kernel / kernel.sum()    # weights hv to sum to 1 or the image gets brighter/darker

def conv(img, kernel, stride=1, padding=0):
    kh, kw = kernel.shape
    padded = pad(img, padding).astype(numpy.float64)
    ph, pw = padded.shape

    # output size is N+2*P-K // stride+1
    out_h = (ph - kh) // stride + 1
    out_w = (pw - kw) // stride + 1
    out = numpy.zeros((out_h, out_w))

    for m in range(kh):
        for n in range(kw):
            shifted = padded[m : m + stride*out_h : stride,
                             n : n + stride*out_w : stride]
            out += shifted * kernel[m, n]

    return numpy.clip(numpy.round(out), 0, 255).astype(numpy.uint8)

def gaussian_filter(img, k, sigma, stride=1, padding=0):
    return conv(img, gaussian_kernel(k, sigma), stride, padding)

# Q4
def histogram(img):
    counts = numpy.zeros(256, dtype=numpy.int64)

    # how many times each pixel val shows up?
    for p in img.ravel():
        counts[p] += 1

    return counts

def save_histogram(img, title, path):
    counts = histogram(img)

    plt.figure(figsize=(8, 4))
    plt.bar(range(256), counts, width=1)
    plt.xlim(-1, 256)
    plt.xlabel("pixel value")
    plt.ylabel("count")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

# PSNR
def psnr(clean, img):
    if clean.shape != img.shape:
        return None
    mse = numpy.mean((clean.astype(numpy.float64) - img.astype(numpy.float64)) ** 2)
    if mse == 0:
        return float("inf")

    return 10 * numpy.log10(255**2 / mse)

def print_psnr(name, clean, img):
    score = psnr(clean, img)
    if score is None:
        print(f"{name}: size {img.shape} != clean {clean.shape}, cant compute psnr")
    else:
        print(f"{name}: psnr = {score:.2f} dB")

if __name__ == "__main__":
    noisy = cv2.imread("test_img/taipei101_noise.png", cv2.IMREAD_GRAYSCALE)
    clean = cv2.imread("test_img/taipei101_gray.png", cv2.IMREAD_GRAYSCALE)

    print_psnr("noisy", clean, noisy)

    # Q1 output
    Q1_img = median_filter(noisy, Q1_KERNEL, Q1_STRIDE, Q1_PADDING)
    cv2.imwrite("result_img/taipei101_Q1.png", Q1_img)
    print_psnr("Q1", clean, Q1_img)

    # Q2 output
    Q2_img = gaussian_filter(noisy, Q2_KERNEL, Q2_SIGMA, Q2_STRIDE, Q2_PADDING)
    cv2.imwrite("result_img/taipei101_Q2.png", Q2_img)
    print_psnr("Q2", clean, Q2_img)

    # Q3 output
    Q3_img = median_filter(noisy, Q3_MEDIAN_KERNEL, Q3_MEDIAN_STRIDE, Q3_MEDIAN_PADDING)
    Q3_img = gaussian_filter(Q3_img, Q3_GAUSS_KERNEL, Q3_GAUSS_SIGMA, Q3_GAUSS_STRIDE, Q3_GAUSS_PADDING)
    cv2.imwrite("result_img/taipei101_Q3.png", Q3_img)
    print_psnr("Q3", clean, Q3_img)

    # Q4 output
    save_histogram(noisy, "taipei101_noise", "result_img/taipei101_noise-his.png")
    save_histogram(Q1_img, "taipei101_Q1", "result_img/taipei101_Q1-his.png")
    save_histogram(Q2_img, "taipei101_Q2", "result_img/taipei101_Q2-his.png")
    save_histogram(Q3_img, "taipei101_Q3", "result_img/taipei101_Q3-his.png")