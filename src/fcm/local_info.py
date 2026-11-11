"""Local spatial information xi with golden-ratio reward/penalty sets
(Wu et al. 2024, Sec. 3.1, Algorithm 2, Eqs. 5-9).

Idea: in a w x w window, noisy pixels tend to sit at the two ENDS of the sorted
gray values (salt is very bright, pepper very dark). So instead of averaging all
neighbours equally, the neighbours are sorted and
  * the middle ~61.8 % (golden ratio) form the REWARD set -> weight x (1 + sigma)
  * the rest (both ends) form the PENALTY set             -> weight x (1 - sigma)
Penalty pixels are down-weighted, not thrown away, so true edges keep some say.

For the centre pixel i and a neighbour j (j != i):
    S_ij  = exp(-(x_j - x_i)^2 / tau_i^2),  tau_i^2 = sum_p (x_p - x_i)^2 / N_R   (Eq. 6)
    Sg_ij = (1 + sigma) S_ij  if j in reward set, (1 - sigma) S_ij otherwise    (Eq. 5)
    Ss_ij = exp(-d_ij), d_ij = Euclidean distance between pixel positions       (Eq. 7)
    SS_ij = Sg_ij * Ss_ij,  SS_ii = 0                                           (Eq. 8)
    xi_i  = sum_j SS_ij x_j / sum_j SS_ij                                       (Eq. 9)
N_R = w*w is the number of pixels in the window (the centre adds 0 to the sum).

Implementation choices (docs/06_KARARLAR.md):
  * reward-set size = floor(0.618 * (N_R - 1))  (D-014; the text says ceil, Fig. 1 shows floor);
    the reward set is the middle block of the sorted list; if the penalty count
    is odd, the extra penalty pixel is at the high end;
  * ties in the sort keep raster order (stable sort);
  * image borders: symmetric (mirror) padding;
  * flat window (tau_i = 0, all neighbours equal the centre): S_ij = 1.
  * Eqs. 5-9 are implemented as written. The similarity values printed in the
    paper's Figs. 2-3 do not follow these equations (D-032); see tests.
"""
from __future__ import annotations

import math

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

GOLDEN = 0.618
_ROUND = {"floor": math.floor, "ceil": math.ceil, "round": round}


def reward_size(n_neighbours: int, ratio: float = GOLDEN, rounding: str = "floor") -> int:
    """Number of pixels in the reward set for n_neighbours = N_R - 1 neighbours."""
    if rounding not in _ROUND:
        raise ValueError(f"rounding must be one of {tuple(_ROUND)}")
    return int(_ROUND[rounding](ratio * n_neighbours))


def reward_mask(values: np.ndarray, ratio: float = GOLDEN, rounding: str = "floor") -> np.ndarray:
    """Boolean mask over the last axis: True where the neighbour is in the reward set.

    `values` has shape (..., n) with the n neighbour gray values of each window.
    """
    n = values.shape[-1]
    k = reward_size(n, ratio, rounding)
    lo = (n - k) // 2
    ranks = np.argsort(np.argsort(values, axis=-1, kind="stable"), axis=-1, kind="stable")
    return (ranks >= lo) & (ranks < lo + k)


def _offsets(w: int) -> tuple[np.ndarray, int]:
    """Row/col offsets of the w*w window in raster order, and the index of the centre."""
    r = w // 2
    dy, dx = np.mgrid[-r : r + 1, -r : r + 1]
    return np.stack([dy.ravel(), dx.ravel()], axis=1), (w * w) // 2


def similarity_weights(center: np.ndarray, neigh: np.ndarray, dist: np.ndarray, sigma: float,
                       ratio: float = GOLDEN, rounding: str = "floor") -> np.ndarray:
    """SS_ij (Eq. 8) for windows given as centre values (...,) and neighbour values (..., n)."""
    n_r = neigh.shape[-1] + 1
    diff2 = (neigh - center[..., None]) ** 2
    tau2 = diff2.sum(axis=-1, keepdims=True) / n_r
    with np.errstate(divide="ignore", invalid="ignore"):
        S = np.where(tau2 > 0, np.exp(-diff2 / np.where(tau2 > 0, tau2, 1.0)), 1.0)   # Eq. 6
    factor = np.where(reward_mask(neigh, ratio, rounding), 1.0 + sigma, 1.0 - sigma)
    return factor * S * np.exp(-dist)                                                # Eqs. 5, 7, 8


def local_spatial_info(img: np.ndarray, w: int = 5, sigma: float = 0.3, ratio: float = GOLDEN,
                       rounding: str = "floor") -> np.ndarray:
    """xi for every pixel of a gray image (Algorithm 2). Same shape as `img`."""
    if w < 3 or w % 2 == 0:
        raise ValueError("w must be an odd window size >= 3")
    if not 0.0 <= sigma < 1.0:
        raise ValueError("sigma must be in [0, 1)")
    img = np.asarray(img, dtype=np.float64)
    r = w // 2
    padded = np.pad(img, r, mode="symmetric")
    win = sliding_window_view(padded, (w, w)).reshape(img.shape + (w * w,))  # (H, W, w*w)
    offs, c = _offsets(w)
    keep = np.arange(w * w) != c
    neigh = win[..., keep]                                    # (H, W, w*w - 1)
    dist = np.hypot(offs[keep, 0], offs[keep, 1]).astype(np.float64)
    SS = similarity_weights(img, neigh, dist, sigma, ratio, rounding)
    return (SS * neigh).sum(axis=-1) / SS.sum(axis=-1)        # Eq. 9
