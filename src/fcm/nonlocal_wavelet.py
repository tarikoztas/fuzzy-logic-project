"""Non-local spatial information theta in the wavelet domain
(Wu et al. 2024, Sec. 3.2, Eqs. 10-11).

Steps:
  1. decompose the image with a one-level dual-tree complex wavelet transform
     (DTCWT): 1 low-frequency sub-image + 6 complex high-frequency sub-images
     (directions +-15, +-45, +-75 degrees);
  2. apply non-local means (NLM) to each of the 7 sub-images:
        r_j = (1/Z_j) * sum_{q in R_j, q != j} y_q * exp(-Gauss[M(y_q) - M(y_j)]^2_{2,v} / (g w^2))   (Eq. 10)
        Z_j = sum_{q in R_j, q != j} exp(-Gauss[M(y_q) - M(y_j)]^2_{2,v} / (g w^2))                 (Eq. 11)
     R_j: S x S search window around j; M(.): w x w patch; Gauss[.]^2_{2,v}: squared
     patch difference weighted by a Gaussian kernel of standard deviation v;
  3. inverse DTCWT -> theta.

Analogy: to repair a damaged letter in a book you look for the same word
elsewhere on the page; pixels whose surroundings look alike vote, no matter
how far apart they are (inside the S x S window).

Implementation (vectorised over the image, one loop over the S*S-1 offsets):
for each offset (dy, dx) the squared difference image between the sub-band and
its shifted copy is filtered with the Gaussian patch kernel, which gives the
patch distance of every pixel to its partner at that offset at once.

Choices (report/decisions.md):
  * D-012: Eq. 10 uses y_q (the text's y_j is a typo).
  * D-010: complex sub-bands: patch distances from the magnitudes |y|, the same
    weights smooth the real and imaginary parts.
  * D-035 (revised): intensities in [0, 1] as in Algorithm 3, step 1 (scale = 1),
    Gaussian patch kernel normalised to sum 1, filtering parameter h^2 = g * w^2
    (= 250 for g = 10, w = 5).
  * D-038 (finding): in [0, 1] units a patch distance is at most ~1, so every weight
    exp(-dist / 250) lies in [0.996, 1]: with the paper's parameters the "non-local
    means" behaves almost exactly like an S x S mean filter on each sub-band.
    `scale` lets the ablation test a truly selective NLM (scale = 255).
  * borders: symmetric padding; one decomposition level; dtcwt defaults
    (near_sym_a / qshift_a filters).
"""
from __future__ import annotations

import cv2
import dtcwt
import numpy as np

_TRANSFORM = dtcwt.Transform2d()


def gaussian_patch_kernel(w: int, upsilon: float) -> np.ndarray:
    """w x w Gaussian weights with standard deviation upsilon, normalised to sum 1."""
    r = w // 2
    yy, xx = np.mgrid[-r : r + 1, -r : r + 1]
    k = np.exp(-(yy**2 + xx**2) / (2.0 * upsilon**2))
    return k / k.sum()


def nlm_subband(band: np.ndarray, S: int = 15, w: int = 5, upsilon: float = 4.0,
                g: float = 10.0) -> np.ndarray:
    """Non-local means of one sub-band (Eqs. 10-11). Real or complex input.

    The centre pixel itself is excluded (q != j), as in Eq. 10.
    """
    if S % 2 == 0 or w % 2 == 0:
        raise ValueError("S and w must be odd")
    band = np.asarray(band)
    is_complex = np.iscomplexobj(band)
    mag = np.abs(band) if is_complex else band.astype(np.float64)
    H, W = mag.shape
    s, r = S // 2, w // 2
    pad = s + r
    mag_p = np.pad(mag, pad, mode="symmetric")
    val_p = np.pad(band, pad, mode="symmetric")
    kernel = gaussian_patch_kernel(w, upsilon)
    h2 = g * w * w
    # centre region (with patch margin r) of the padded magnitude
    centre = mag_p[s : s + H + 2 * r, s : s + W + 2 * r]

    num = np.zeros((H, W), dtype=val_p.dtype)
    Z = np.zeros((H, W), dtype=np.float64)
    for dy in range(-s, s + 1):
        for dx in range(-s, s + 1):
            if dy == 0 and dx == 0:
                continue  # q != j
            shifted = mag_p[s + dy : s + dy + H + 2 * r, s + dx : s + dx + W + 2 * r]
            d2 = (shifted - centre) ** 2
            # Gaussian-weighted patch distance for every pixel (valid part only)
            dist = cv2.filter2D(d2, -1, kernel, borderType=cv2.BORDER_CONSTANT)[r : r + H, r : r + W]
            wgt = np.exp(-dist / h2)
            num += wgt * val_p[pad + dy : pad + dy + H, pad + dx : pad + dx + W]
            Z += wgt
    return num / Z


def nonlocal_wavelet_info(img: np.ndarray, S: int = 15, w: int = 5, upsilon: float = 4.0,
                          g: float = 10.0, scale: float = 1.0) -> np.ndarray:
    """theta for a gray image in [0, 1]: DTCWT -> NLM on all 7 sub-images -> inverse DTCWT."""
    img = np.asarray(img, dtype=np.float64)
    if img.ndim != 2:
        raise ValueError("expects a 2-D gray image")
    H, W = img.shape
    # DTCWT needs even sizes (BSDS500 images are 321 x 481): mirror one row/column, crop at the end
    work = np.pad(img, ((0, H % 2), (0, W % 2)), mode="symmetric")
    pyr = _TRANSFORM.forward(work * scale, nlevels=1)
    low = nlm_subband(pyr.lowpass, S, w, upsilon, g)
    high = np.stack([nlm_subband(pyr.highpasses[0][..., d], S, w, upsilon, g) for d in range(6)], axis=-1)
    out = _TRANSFORM.inverse(dtcwt.Pyramid(low, (high,)))
    return out[:H, :W] / scale
