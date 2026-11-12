"""Classic Fuzzy C-Means (Bezdek 1984) for gray images — Algorithm 1 of the paper.

    J   = sum_i sum_j u_ij^m (y_j - c_i)^2,   sum_i u_ij = 1            (Eq. 1)
    u_ij = 1 / sum_r ( |y_j - c_i| / |y_j - c_r| )^(2/(m-1))             (Eq. 2)
    c_i  = sum_j u_ij^m y_j / sum_j u_ij^m                               (Eq. 3)

Each pixel j is a point y_j (its gray value in [0, 1]); FCM knows nothing about
where the pixel is, which is exactly why it is sensitive to noise.

Iteration (Algorithm 1): random U -> repeat { centers (3), memberships (2),
objective (1) } until |J(a) - J(a-1)| <= eps or a reaches T.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

# A pixel whose value equals a center exactly would give a 0 distance (division by 0
# in Eq. 2). Flooring the squared distance gives that cluster a membership of ~1,
# which is the mathematical limit.
_D2_FLOOR = 1e-12


@dataclass
class FCMResult:
    U: np.ndarray            # memberships, (K, H, W) for an image input, columns sum to 1
    centers: np.ndarray      # (K,)
    J_history: list[float] = field(default_factory=list)
    n_iter: int = 0
    time_s: float = 0.0      # clustering time only (pre-processing is timed separately)

    @property
    def labels(self) -> np.ndarray:
        """Defuzzified segmentation: label_j = argmax_i u_ij."""
        return np.argmax(self.U, axis=0)


def init_membership(K: int, N: int, seed: int) -> np.ndarray:
    """Random initial U (K x N) with columns summing to 1.

    Shared by FCM and the proposed method, so with the same seed both start
    from the same memberships (fair comparison, D-015 in report/decisions.md).
    """
    rng = np.random.default_rng(seed)
    U = rng.random((K, N))
    return U / U.sum(axis=0, keepdims=True)


def update_centers(U: np.ndarray, y: np.ndarray, m: float) -> np.ndarray:
    """Eq. (3): membership-weighted mean of the pixel values."""
    Um = U**m
    return (Um @ y) / Um.sum(axis=1)


def update_memberships(d2: np.ndarray, m: float) -> np.ndarray:
    """Eq. (2) written with squared distances d2 (K x N).

    (|y-c_i| / |y-c_r|)^(2/(m-1)) = (d2_i / d2_r)^(1/(m-1)), so
    u_ij = d2_ij^(-1/(m-1)) / sum_r d2_rj^(-1/(m-1)).
    """
    inv = np.maximum(d2, _D2_FLOOR) ** (-1.0 / (m - 1.0))
    return inv / inv.sum(axis=0, keepdims=True)


def objective(U: np.ndarray, d2: np.ndarray, m: float) -> float:
    """Eq. (1)."""
    return float(np.sum(U**m * d2))


def fcm(img: np.ndarray, K: int, m: float = 2.0, T: int = 100, eps: float = 1e-6,
        seed: int = 0) -> FCMResult:
    """Run FCM on a gray image scaled to [0, 1]. Returns U with the image's shape (K, H, W)."""
    if m <= 1.0:
        raise ValueError("fuzzifier m must be > 1")
    img = np.asarray(img, dtype=np.float64)
    y = img.ravel()
    U = init_membership(K, y.size, seed)

    t0 = time.perf_counter()
    J_hist: list[float] = []
    a = 0
    while True:
        a += 1
        c = update_centers(U, y, m)                 # Eq. 3
        d2 = (y[None, :] - c[:, None]) ** 2         # (K, N) squared distances
        U = update_memberships(d2, m)               # Eq. 2
        J_hist.append(objective(U, d2, m))          # Eq. 1
        if (a > 1 and abs(J_hist[-1] - J_hist[-2]) <= eps) or a >= T:
            break
    elapsed = time.perf_counter() - t0
    return FCMResult(U=U.reshape((K,) + img.shape), centers=c, J_history=J_hist,
                     n_iter=a, time_s=elapsed)
