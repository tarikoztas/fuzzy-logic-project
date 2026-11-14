"""Second iteration of the contribution, candidate C (D-044/D-045): a fuzzy rule base
that chooses the reward factor sigma of the local term.

Why: in the single-factor ablation (C2) the reward factor sigma of Eq. 5 was the most
influential under-determined quantity: the paper's sigma = 0.3 is fine at low noise,
a larger sigma (stronger reward/penalty contrast, i.e. outliers in the window count
less) closes most of the high-noise gap. A fixed number cannot be right for every
image, so a small Mamdani system picks sigma from how noisy the image looks.

Input  NoiseLevel  (image level): robust noise estimate from the finest diagonal
       Haar wavelet coefficients, sigma_n = median(|HH|) / 0.6745 (the classical
       median-absolute-deviation estimator of Donoho and Johnstone). Flat image
       regions give HH = 0, so mainly noise contributes.
   or  LocalNoise  (pixel level): mean over a w x w window of |y - median3x3(y)|,
       i.e. how much impulse-like deviation there is around the pixel.
Output Sigma, universe [0, 1.2] (clipped to [0, 0.95]; Eq. 5 needs sigma < 1).

Rules (one input, three terms):
    IF noise is Low    THEN sigma is Small    (keep the paper's mild reward/penalty)
    IF noise is Medium THEN sigma is Medium
    IF noise is High   THEN sigma is Large    (penalise the extremes of the window strongly)
Mamdani: min implication, max aggregation, centroid defuzzification (our engine, src/fuzzy).
The output sets are symmetric triangles, so a fully fired single rule returns exactly
the centre of its set (e.g. 0.3 for Small).
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import median_filter, uniform_filter

from src.fuzzy import FIS, MF, Rule, Variable

MAD_TO_STD = 0.6745  # median(|N(0,1)|)


def _gray(y: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=np.float64)
    return y.mean(axis=-1) if y.ndim == 3 else y


def noise_estimate(y: np.ndarray) -> float:
    """Image-level noise level: median(|HH|) / 0.6745 of the one-level Haar transform (gray or colour)."""
    g = _gray(y)
    h, w = g.shape
    g = g[: h // 2 * 2, : w // 2 * 2]
    hh = (g[0::2, 0::2] - g[0::2, 1::2] - g[1::2, 0::2] + g[1::2, 1::2]) / 2.0
    return float(np.median(np.abs(hh)) / MAD_TO_STD)


def local_noise(y: np.ndarray, w: int = 5) -> np.ndarray:
    """Pixel-level noise indicator: window mean of |y - median3x3(y)| (gray or colour -> (H, W))."""
    g = _gray(y)
    imp = np.abs(g - median_filter(g, size=3, mode="mirror"))
    return uniform_filter(imp, size=w, mode="mirror")


def build_sigma_fis(breaks: tuple[float, float, float], out: tuple[float, float, float] = (0.3, 0.6, 0.9),
                    universe: float = 0.5) -> FIS:
    """breaks = (low, mid, high): Low is full up to `low`, Medium peaks at `mid`, High is full from `high`."""
    lo, mid, hi = breaks
    if not 0 <= lo < mid < hi <= universe:
        raise ValueError("breaks must satisfy 0 <= low < mid < high <= universe")
    s, m, l = out
    noise = Variable("Noise", (0.0, universe), {
        "Low": MF("trap", 0.0, 0.0, lo, mid),
        "Medium": MF("tri", lo, mid, hi),
        "High": MF("trap", mid, hi, universe, universe),
    })
    d = max(m - s, l - m)
    sigma = Variable("Sigma", (0.0, 1.2), {
        "Small": MF("tri", s - d, s, s + d),
        "Medium": MF("tri", m - d, m, m + d),
        "Large": MF("tri", l - d, l, l + d),
    }, resolution=241)
    rules = [Rule({"Noise": a}, {"Sigma": c}) for a, c in (("Low", "Small"), ("Medium", "Medium"), ("High", "Large"))]
    return FIS([noise], [sigma], rules, kind="mamdani", defuzz="centroid")


class FuzzySigma:
    """sigma_rule for src/fcm/pipeline.run_asrfcm: y -> sigma (a number, or (H, W) per pixel)."""

    def __init__(self, level: str = "image", breaks=(0.05, 0.15, 0.25), out=(0.3, 0.6, 0.9), w: int = 5):
        if level not in ("image", "pixel"):
            raise ValueError("level must be 'image' or 'pixel'")
        self.level, self.w = level, w
        self.fis = build_sigma_fis(tuple(breaks), tuple(out))
        self.label = f"FIS-sigma-{level}-{breaks}-{out}"

    def inputs(self, y: np.ndarray):
        return noise_estimate(y) if self.level == "image" else local_noise(y, self.w)

    def __call__(self, y: np.ndarray):
        x = self.inputs(y)
        s = self.fis.evaluate(Noise=np.atleast_1d(x))["Sigma"]
        s = np.clip(s, 0.0, 0.95)
        return float(s[0]) if self.level == "image" else s.reshape(np.shape(x))
