"""Sparse-regularised FCM with complementary spatial information
(Wu et al. 2024, Sec. 3.4, Algorithm 3, Eqs. 20-29).

Objective (Eq. 20):
    J = sum_i sum_j u_ij^m d_ij + delta * ||U||_0,
    d_ij = alpha_j (y_j - c_i)^2 + beta_j (xi_j - c_i)^2 + gamma_j (theta_j - c_i)^2

The l0 term counts non-zero memberships, so it pushes U towards "each pixel
belongs to one cluster". It is solved in three steps per iteration
(framework of Wang et al. 2021, SRFCM):
  1. centres c (Eq. 29) and "rough" memberships eta (Eq. 28) as in FCM;
  2. hard threshold: eta_ij < sqrt(delta) -> 0 (Eqs. 24-26);
  3. normalise every column to sum 1 (Eq. 27).
Stop when |J(a) - J(a-1)| <= eps or a reaches T.

Choices (report/decisions.md):
  * D-011 empty columns: with delta = 0.4, sqrt(delta) = 0.632 > 0.5, so at most one
    membership per pixel can pass the threshold; for many pixels none does.
    Policies: "keep" - leave that pixel's eta unthresholded; "argmax" - keep only its
    largest eta (the pixel becomes crisp). Default fixed by experiment E2 (D-036).
  * D-036 the centre update (Eq. 29) uses the current membership matrix U
    (after thresholding and normalisation) of the previous iteration.
  * D-037 ablation switches (Table 1): local / non-local information off -> the
    term and its coefficient are dropped; coefficients come from the active terms
    only; sparse off -> no thresholding (delta = 0 in Eq. 20).
"""
from __future__ import annotations

import time

import numpy as np

from .baseline_fcm import FCMResult, init_membership

_D_FLOOR = 1e-12


def sparse_fcm(y: np.ndarray, xi: np.ndarray | None, theta: np.ndarray | None,
               alpha: np.ndarray, beta: np.ndarray | None, gamma: np.ndarray | None,
               K: int, m: float = 2.0, delta: float = 0.4, T: int = 100, eps: float = 1e-6,
               seed: int = 0, empty_col_policy: str = "keep") -> FCMResult:
    """Algorithm 3. Pass xi/beta = None (or theta/gamma = None) to drop a term (ablation).

    All image-shaped inputs are flattened internally; U is returned as (K, H, W).
    delta = 0 disables the sparse step (plain FCM with the complementary terms).
    """
    if empty_col_policy not in ("keep", "argmax"):
        raise ValueError("empty_col_policy must be 'keep' or 'argmax'")
    shape = np.shape(y)
    terms = [(np.ravel(alpha), np.ravel(y))]
    if xi is not None:
        terms.append((np.ravel(beta), np.ravel(xi)))
    if theta is not None:
        terms.append((np.ravel(gamma), np.ravel(theta)))
    weight_sum = sum(w for w, _ in terms)          # alpha + beta + gamma
    weighted_x = sum(w * x for w, x in terms)      # alpha*y + beta*xi + gamma*theta
    N = weight_sum.size
    U = init_membership(K, N, seed)
    thr = np.sqrt(delta)

    t0 = time.perf_counter()
    J_hist: list[float] = []
    a = 0
    while True:
        a += 1
        Um = U**m
        c = (Um @ weighted_x) / (Um @ weight_sum)                        # Eq. 29
        d = sum(w[None, :] * (x[None, :] - c[:, None]) ** 2 for w, x in terms)  # (K, N)
        inv = np.maximum(d, _D_FLOOR) ** (-1.0 / (m - 1.0))
        eta = inv / inv.sum(axis=0, keepdims=True)                       # Eq. 28
        if delta > 0:
            U_t = np.where(eta >= thr, eta, 0.0)                         # Eqs. 24-26
            empty = U_t.sum(axis=0) == 0
            if empty.any():                                              # D-011
                if empty_col_policy == "keep":
                    U_t[:, empty] = eta[:, empty]
                else:
                    best = np.argmax(eta[:, empty], axis=0)
                    U_t[best, np.flatnonzero(empty)] = eta[best, np.flatnonzero(empty)]
            U = U_t / U_t.sum(axis=0, keepdims=True)                     # Eq. 27
        else:
            U = eta
        J = float(np.sum(U**m * d) + delta * np.count_nonzero(U))       # Eq. 20
        J_hist.append(J)
        if (a > 1 and abs(J_hist[-1] - J_hist[-2]) <= eps) or a >= T:
            break
    elapsed = time.perf_counter() - t0
    return FCMResult(U=U.reshape((K,) + tuple(shape)), centers=c, J_history=J_hist,
                     n_iter=a, time_s=elapsed)
