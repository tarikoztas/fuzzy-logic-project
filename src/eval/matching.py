"""Cluster-to-class matching.

Clustering returns arbitrary cluster numbers (cluster 0 may be the "white"
region in one run and the "black" region in another). Before computing ACC,
F-score or Kappa we must decide which cluster corresponds to which
ground-truth class. The paper does not describe its protocol (docs/02 §9-11);
we use the standard choice: the one-to-one mapping that maximises the number of
correctly labelled pixels, found with the Hungarian algorithm
(`scipy.optimize.linear_sum_assignment`).

NMI does not need matching (it is invariant to renaming the clusters).
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment


def confusion_matrix(gt: np.ndarray, pred: np.ndarray, n_gt: int | None = None,
                     n_pred: int | None = None) -> np.ndarray:
    """C[a, b] = number of pixels with ground-truth class a and predicted cluster b."""
    gt = np.asarray(gt).ravel().astype(np.int64)
    pred = np.asarray(pred).ravel().astype(np.int64)
    if gt.shape != pred.shape:
        raise ValueError("gt and pred must have the same number of pixels")
    n_gt = int(gt.max()) + 1 if n_gt is None else n_gt
    n_pred = int(pred.max()) + 1 if n_pred is None else n_pred
    C = np.zeros((n_gt, n_pred), dtype=np.int64)
    np.add.at(C, (gt, pred), 1)
    return C


def match_labels(gt: np.ndarray, pred: np.ndarray) -> tuple[np.ndarray, dict[int, int]]:
    """Rename the clusters in `pred` to the ground-truth classes they overlap most (one-to-one).

    Returns (relabelled prediction with the shape of `pred`, mapping cluster -> class).
    If there are more clusters than classes, unmatched clusters get new labels
    (n_gt, n_gt+1, ...), so their pixels count as errors.
    """
    pred = np.asarray(pred)
    C = confusion_matrix(gt, pred)
    rows, cols = linear_sum_assignment(C, maximize=True)  # rows: classes, cols: clusters
    mapping = {int(c): int(r) for r, c in zip(rows, cols)}
    next_label = C.shape[0]
    for c in range(C.shape[1]):
        if c not in mapping:
            mapping[c] = next_label
            next_label += 1
    lut = np.array([mapping[c] for c in range(C.shape[1])], dtype=np.int64)
    return lut[pred.astype(np.int64)], mapping
