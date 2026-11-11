"""Synthetic test images sy1, sy2, sy3 (Wu et al. 2024, Fig. 9).

The label maps in `data/synthetic/` were re-created from the paper's figure by
`tools/extract_synthetic_from_figure.py`; they follow the paper's shapes and
gray levels but are NOT the authors' original files (the paper does not
publish them). Report this difference.

Each image is piecewise constant: every pixel of class k has gray value
LEVELS[name][k] / 255, so the clean image and its ground truth come from the
same label map.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "synthetic"

# Gray levels measured in Fig. 9 (0..255). The number of levels is the number of clusters K.
LEVELS: dict[str, tuple[int, ...]] = {
    "sy1": (0, 255),
    "sy2": (0, 107, 255),
    "sy3": (0, 107, 222),
}
NAMES = tuple(LEVELS)


@dataclass(frozen=True)
class SyntheticImage:
    name: str
    image: np.ndarray   # float64 in [0, 1], shape (256, 256), noise-free
    labels: np.ndarray  # int, shape (256, 256), values 0..K-1 (ground truth)
    K: int


def load(name: str, data_dir: Path = DATA_DIR) -> SyntheticImage:
    """Load a noise-free synthetic image and its ground-truth labels."""
    if name not in LEVELS:
        raise ValueError(f"unknown synthetic image {name!r}; choose from {NAMES}")
    path = data_dir / f"{name}_labels.png"
    labels = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if labels is None:
        raise FileNotFoundError(path)
    levels = np.asarray(LEVELS[name], dtype=np.float64) / 255.0
    K = len(levels)
    if labels.max() >= K:
        raise ValueError(f"{path} has label {labels.max()} but K={K}")
    labels = labels.astype(np.int64)
    return SyntheticImage(name=name, image=levels[labels], labels=labels, K=K)
