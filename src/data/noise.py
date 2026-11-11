"""Noise models used to corrupt the test images.

All functions take a float image in [0, 1] and return a new float image clipped
to [0, 1], following the definitions of MATLAB's `imnoise` (a common choice
in FCM segmentation papers; the paper itself does not give its noise code).

Paper (Sec. 4.3): "a composite noise profile consisting of equal proportions of
Gaussian, salt-and-pepper, and multiplicative noise". It does not define the
noise *level* precisely. Our reading (decision D-027, `docs/06_KARARLAR.md`):

    "p % mixed noise"  =  Gaussian(mean 0, variance p)
                        -> multiplicative/speckle(variance p)
                        -> salt-and-pepper(density p)

i.e. the three noises are applied one after another with the *same* parameter
p ("equal proportions"). A level of 5 % means p = 0.05. Every function draws
its random numbers from a `numpy.random.Generator`, so a fixed seed always
gives the same noisy image.
"""
from __future__ import annotations

import numpy as np

KINDS = ("gaussian", "speckle", "salt_pepper", "mixed")
MIXED_ORDER = ("gaussian", "speckle", "salt_pepper")


def gaussian(img: np.ndarray, var: float, rng: np.random.Generator, mean: float = 0.0) -> np.ndarray:
    """Additive Gaussian noise: J = I + n, n ~ N(mean, var)."""
    out = img + rng.normal(mean, np.sqrt(var), size=img.shape)
    return np.clip(out, 0.0, 1.0)


def speckle(img: np.ndarray, var: float, rng: np.random.Generator) -> np.ndarray:
    """Multiplicative (speckle) noise: J = I + n*I, n uniform with mean 0 and variance `var`.

    A uniform variable on [-a, a] has variance a^2/3, so a = sqrt(3*var).
    Note: black pixels (I = 0) are not changed by multiplicative noise.
    """
    a = np.sqrt(3.0 * var)
    n = rng.uniform(-a, a, size=img.shape)
    return np.clip(img + n * img, 0.0, 1.0)


def salt_pepper(img: np.ndarray, density: float, rng: np.random.Generator) -> np.ndarray:
    """Impulse noise: a fraction `density` of the pixels is replaced, half by 0 (pepper), half by 1 (salt)."""
    x = rng.random(img.shape)
    out = img.copy()
    out[x < density / 2] = 0.0
    out[(x >= density / 2) & (x < density)] = 1.0
    return out


def mixed(img: np.ndarray, p: float, rng: np.random.Generator) -> np.ndarray:
    """Paper's mixed noise (our reading, see module docstring): the three noises in turn with parameter p."""
    out = img
    for kind in MIXED_ORDER:
        out = _SINGLE[kind](out, p, rng)
    return out


_SINGLE = {"gaussian": gaussian, "speckle": speckle, "salt_pepper": salt_pepper}


def add_noise(img: np.ndarray, kind: str, level: float, seed: int) -> np.ndarray:
    """Corrupt `img` with noise `kind` at `level` (a fraction: 0.05 means 5 %), reproducibly.

    The same (img, kind, level, seed) always returns the same array.
    """
    if kind not in KINDS:
        raise ValueError(f"unknown noise kind {kind!r}; choose from {KINDS}")
    if not 0.0 <= level <= 1.0:
        raise ValueError(f"level must be a fraction in [0, 1], got {level}")
    img = np.asarray(img, dtype=np.float64)
    if img.min() < 0.0 or img.max() > 1.0:
        raise ValueError("image must be scaled to [0, 1]")
    rng = np.random.default_rng(seed)
    if level == 0.0:
        return img.copy()
    if kind == "mixed":
        return mixed(img, level, rng)
    return _SINGLE[kind](img, level, rng)
