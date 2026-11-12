"""Evaluation metrics of the paper (Sec. 4.2, Eqs. 30-35), all returned in percent.

Two groups:
  * fuzzy-partition quality, computed from the membership matrix U (no ground truth):
      V_PC (Eq. 30, larger = crisper), V_PE (Eq. 31, smaller = crisper);
  * agreement with the ground truth, computed from the crisp label map
    (label = argmax_i u_ij, i.e. defuzzification):
      ACC (Eq. 32), F-score (Eq. 33), NMI (Eq. 34), Kappa (Eq. 35).

Protocol choices the paper does not state (documented in D-028):
  * clusters are matched to classes with the Hungarian algorithm (matching.py);
  * F-score is the *macro* average of the per-class F = 2TP / (2TP + FP + FN);
  * NMI uses natural logarithms (the ratio does not depend on the base).
  * Kappa is Cohen's kappa; `kappa_paper` reproduces how the paper's Kappa
    numbers behave for K > 2 (D-031) and is used only for comparison with it.
"""
from __future__ import annotations

import numpy as np

from .matching import confusion_matrix, match_labels


def _as_KN(U: np.ndarray) -> np.ndarray:
    """Accept U as (K, N) or (K, H, W)."""
    U = np.asarray(U, dtype=np.float64)
    return U.reshape(U.shape[0], -1)


def vpc(U: np.ndarray) -> float:
    """Partition coefficient, Eq. (30): (1/N) * sum_i sum_j u_ij^2 * 100."""
    U = _as_KN(U)
    return float(np.sum(U**2) / U.shape[1] * 100.0)


def vpe(U: np.ndarray) -> float:
    """Partition entropy, Eq. (31): -(1/N) * sum_i sum_j u_ij ln(u_ij) * 100, with 0*ln(0) = 0.

    The convention 0*ln(0) = 0 matters for the sparse method, whose U contains exact zeros.
    """
    U = _as_KN(U)
    pos = U > 0
    return float(-np.sum(U[pos] * np.log(U[pos])) / U.shape[1] * 100.0) + 0.0  # +0.0 avoids "-0.0"


def _square_confusion(gt: np.ndarray, pred_matched: np.ndarray) -> np.ndarray:
    n = int(max(gt.max(), pred_matched.max())) + 1
    return confusion_matrix(gt, pred_matched, n, n)


def accuracy(gt: np.ndarray, pred: np.ndarray) -> float:
    """Eq. (32): share of pixels whose (matched) cluster equals the true class."""
    gt = np.asarray(gt).ravel()
    matched, _ = match_labels(gt, np.asarray(pred).ravel())
    return float(np.mean(matched == gt) * 100.0)


def f_score(gt: np.ndarray, pred: np.ndarray) -> float:
    """Eq. (33), macro-averaged over the ground-truth classes."""
    gt = np.asarray(gt).ravel()
    matched, _ = match_labels(gt, np.asarray(pred).ravel())
    C = _square_confusion(gt, matched)
    scores = []
    for k in range(int(gt.max()) + 1):
        tp = C[k, k]
        fp = C[:, k].sum() - tp
        fn = C[k, :].sum() - tp
        denom = 2 * tp + fp + fn
        scores.append(2 * tp / denom if denom > 0 else 1.0)
    return float(np.mean(scores) * 100.0)


def nmi(gt: np.ndarray, pred: np.ndarray) -> float:
    """Eq. (34): 2*MI(gt, pred) / (H(gt) + H(pred)). No matching needed."""
    C = confusion_matrix(gt, pred).astype(np.float64)
    P = C / C.sum()                      # joint distribution
    pa, pb = P.sum(axis=1), P.sum(axis=0)  # marginals
    nz = P > 0
    mi = np.sum(P[nz] * np.log(P[nz] / np.outer(pa, pb)[nz]))
    ha = -np.sum(pa[pa > 0] * np.log(pa[pa > 0]))
    hb = -np.sum(pb[pb > 0] * np.log(pb[pb > 0]))
    if ha + hb == 0:  # both label maps constant -> identical partitions
        return 100.0
    return float(2.0 * mi / (ha + hb) * 100.0)


def kappa(gt: np.ndarray, pred: np.ndarray) -> float:
    """Eq. (35): Cohen's kappa (p0 - pe) / (1 - pe) after matching.

    p0 = observed agreement (= ACC); pe = agreement expected by chance from the
    class/cluster sizes alone.
    """
    gt = np.asarray(gt).ravel()
    matched, _ = match_labels(gt, np.asarray(pred).ravel())
    C = _square_confusion(gt, matched).astype(np.float64)
    n = C.sum()
    p0 = np.trace(C) / n
    pe = np.sum(C.sum(axis=1) * C.sum(axis=0)) / n**2
    if pe == 1.0:
        return 100.0 if p0 == 1.0 else 0.0
    return float((p0 - pe) / (1.0 - pe) * 100.0)


def kappa_paper(gt: np.ndarray, pred: np.ndarray, K: int | None = None) -> float:
    """Kappa as the paper's reported numbers behave (reverse-engineered, D-031).

    Solving Eq. (35) for p_e with the paper's own ACC and Kappa values gives
    p_e = 0.5556 for every 3-class cell of Tables 4 and 7 (all images, all noise
    levels, FCM and Ours), i.e. p_e does not depend on the prediction at all.
    The constant fits  p_e = (1/K)^2 + ((K-1)/K)^2  (1/2 for K=2, 5/9 for K=3).
    So the paper's "Kappa" is a fixed rescaling of ACC, not Cohen's kappa.
    We use it ONLY to compare with the paper; `kappa` above is the correct one.
    """
    gt = np.asarray(gt).ravel()
    K = int(gt.max()) + 1 if K is None else K
    p0 = accuracy(gt, pred) / 100.0
    pe = (1.0 / K) ** 2 + ((K - 1.0) / K) ** 2
    return float((p0 - pe) / (1.0 - pe) * 100.0)


def defuzzify(U: np.ndarray) -> np.ndarray:
    """Crisp labels from memberships: label_j = argmax_i u_ij (shape of U without its first axis)."""
    U = np.asarray(U)
    return np.argmax(U, axis=0)


def evaluate(gt: np.ndarray, U: np.ndarray | None = None, pred: np.ndarray | None = None) -> dict[str, float]:
    """All six metrics. Give U (pred is then argmax U) or pred (then V_PC/V_PE are NaN)."""
    if pred is None:
        if U is None:
            raise ValueError("give U or pred")
        pred = defuzzify(U)
    out = {
        "VPC": vpc(U) if U is not None else float("nan"),
        "VPE": vpe(U) if U is not None else float("nan"),
        "ACC": accuracy(gt, pred),
        "F": f_score(gt, pred),
        "NMI": nmi(gt, pred),
        "Kappa": kappa(gt, pred),
        "Kappa_paper": kappa_paper(gt, pred),
    }
    return out
