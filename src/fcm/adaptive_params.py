"""Adaptive constraint coefficients alpha, beta, gamma (Wu et al. 2024, Sec. 3.3, Eqs. 13-19).

In the objective (Eq. 12/20) every pixel j has three distance terms:
    alpha_j |y_j - c_i|^2 + beta_j |xi_j - c_i|^2 + gamma_j |theta_j - c_i|^2
(original image, local information, non-local information). If a pixel differs
a lot from its corrected versions xi and theta, it is probably noisy, so the
original value should count less (small alpha) and the corrected ones more.

Paper:
    dG1 = k * exp(y_j - xi_j)    + eps                                   (Eq. 15)
    dG2 = k * exp(y_j - theta_j) + eps                                   (Eq. 16)
    alpha_j = 1 / (dG1 + dG2),  beta_j = dG1,  gamma_j = dG2              (Eqs. 17-19)
(Eqs. 13-14 first define dG with |y - xi|; Eqs. 15-16 then redefine them with
the exponential, which is what Eqs. 17-19 use.)

Note on scale: with gray values in [0, 1] and k = 15, dG lies in
[15/e, 15e] ~ [5.5, 40.8], so alpha ~ 0.01-0.1 while beta, gamma ~ 5-40:
the corrected images dominate the clustering for every pixel.

Variants (D-013):
    "signed" - Eqs. 15-16 as printed: exp(y - xi). Salt (y > xi) raises dG,
               pepper (y < xi) lowers it below k, an asymmetry the text does not discuss.
    "abs"    - exp(|y - xi|), the "absolute difference" the text describes.
The fuzzy-rule alternative (D-033) lives in src/fcm/fis_coefficients.py and
returns the same (alpha, beta, gamma) triple, so the clustering code can take
either provider.
"""
from __future__ import annotations

import numpy as np

EPS = 1e-8


def paper_coefficients(y: np.ndarray, xi: np.ndarray, theta: np.ndarray, k: float = 15.0,
                       variant: str = "signed", eps: float = EPS) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """alpha, beta, gamma of Eqs. 15-19 (arrays with the image's shape)."""
    if variant not in ("signed", "abs"):
        raise ValueError("variant must be 'signed' or 'abs'")
    d1 = y - xi
    d2 = y - theta
    if variant == "abs":
        d1, d2 = np.abs(d1), np.abs(d2)
    dG1 = k * np.exp(d1) + eps  # Eq. 15
    dG2 = k * np.exp(d2) + eps  # Eq. 16
    alpha = 1.0 / (dG1 + dG2)   # Eq. 17
    return alpha, dG1, dG2      # Eqs. 18-19: beta = dG1, gamma = dG2


def absolute_differences(y: np.ndarray, xi: np.ndarray, theta: np.ndarray, eps: float = EPS
                         ) -> tuple[np.ndarray, np.ndarray]:
    """Eqs. 13-14: |y - xi| + eps and |y - theta| + eps (inputs of the fuzzy-rule variant)."""
    return np.abs(y - xi) + eps, np.abs(y - theta) + eps
