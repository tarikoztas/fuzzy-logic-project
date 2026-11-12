"""Defuzzification: turn an aggregated output fuzzy set mu(z) over a sampled
universe z into one crisp number (vectorised over many sets at once).

Each function takes z (U,) and mu (N, U) and returns (N,).
If a row of mu is all zero (no rule fired), the middle of the universe is returned.
"""
from __future__ import annotations

import numpy as np


def _empty(mu: np.ndarray) -> np.ndarray:
    return mu.max(axis=1) <= 0


def centroid(z: np.ndarray, mu: np.ndarray) -> np.ndarray:
    """Centre of gravity: sum(z * mu) / sum(mu)."""
    s = mu.sum(axis=1)
    out = (mu @ z) / np.where(s > 0, s, 1.0)
    return np.where(_empty(mu), 0.5 * (z[0] + z[-1]), out)


def bisector(z: np.ndarray, mu: np.ndarray) -> np.ndarray:
    """The z that splits the area under mu into two equal halves."""
    cum = np.cumsum(mu, axis=1)
    half = cum[:, -1:] / 2.0
    idx = np.argmax(cum >= half, axis=1)
    out = z[idx]
    return np.where(_empty(mu), 0.5 * (z[0] + z[-1]), out)


def mean_of_maxima(z: np.ndarray, mu: np.ndarray, tol: float = 1e-9) -> np.ndarray:
    """Mean of the z values where mu reaches its maximum."""
    peak = mu.max(axis=1, keepdims=True)
    at_max = mu >= peak - tol
    out = (at_max @ z) / at_max.sum(axis=1)
    return np.where(_empty(mu), 0.5 * (z[0] + z[-1]), out)


METHODS = {"centroid": centroid, "bisector": bisector, "mom": mean_of_maxima}
