"""Membership functions mu(x) in [0, 1] (vectorised over x).

A fuzzy set assigns every value x a degree of membership. "Small difference"
is not a yes/no property: 0.02 is fully small, 0.10 partly small, 0.30 not small.
"""
from __future__ import annotations

import numpy as np


def trimf(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    """Triangle with feet a, c and peak b (a == b or b == c gives a shoulder)."""
    x = np.asarray(x, dtype=np.float64)
    left = np.ones_like(x) if b == a else (x - a) / (b - a)
    right = np.ones_like(x) if c == b else (c - x) / (c - b)
    y = np.minimum(left, right)
    y = np.where(x == b, 1.0, y)
    return np.clip(y, 0.0, 1.0)


def trapmf(x: np.ndarray, a: float, b: float, c: float, d: float) -> np.ndarray:
    """Trapezoid: rises a->b, equals 1 on [b, c], falls c->d."""
    x = np.asarray(x, dtype=np.float64)
    left = np.ones_like(x) if b == a else (x - a) / (b - a)
    right = np.ones_like(x) if d == c else (d - x) / (d - c)
    y = np.minimum(np.minimum(left, right), 1.0)
    y = np.where((x >= b) & (x <= c), 1.0, y)
    return np.clip(y, 0.0, 1.0)


def gaussmf(x: np.ndarray, mean: float, sigma: float) -> np.ndarray:
    """Gaussian bell exp(-(x - mean)^2 / (2 sigma^2))."""
    x = np.asarray(x, dtype=np.float64)
    return np.exp(-((x - mean) ** 2) / (2.0 * sigma**2))


def shoulder_gaussmf(x: np.ndarray, mean: float, sigma: float, side: str) -> np.ndarray:
    """Gaussian that stays at 1 beyond its mean on one side ('left' or 'right')."""
    x = np.asarray(x, dtype=np.float64)
    g = gaussmf(x, mean, sigma)
    return np.where(x <= mean, 1.0, g) if side == "left" else np.where(x >= mean, 1.0, g)


class MF:
    """A named membership function: MF('tri', 0, 0.2, 0.35)(x)."""

    _KINDS = {"tri": trimf, "trap": trapmf, "gauss": gaussmf,
              "gauss_left": lambda x, m, s: shoulder_gaussmf(x, m, s, "left"),
              "gauss_right": lambda x, m, s: shoulder_gaussmf(x, m, s, "right")}

    def __init__(self, kind: str, *params: float):
        if kind not in self._KINDS:
            raise ValueError(f"unknown membership function {kind!r}")
        self.kind, self.params = kind, params

    def __call__(self, x: np.ndarray) -> np.ndarray:
        return self._KINDS[self.kind](x, *self.params)

    def __repr__(self) -> str:
        return f"{self.kind}{self.params}"
