"""BSDS500 loader for the eight real images used in the paper (Fig. 22, Table 9).

Source: Berkeley Segmentation Data Set and Benchmark (BSDS500), Arbelaez et al.,
IEEE TPAMI 33(5), 2011 (references/README.md [7]). Archive:
https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/grouping/BSR/BSR_bsds500.tgz
Extract it so that `data/raw/BSR/BSDS500/data/{images,groundTruth}/...` exists
(see data/README.md). The data is not committed to git.

Protocol (decision D-029):
  * colour -> gray: ITU-R BT.601 luma, 0.2989 R + 0.5870 G + 0.1140 B
    (the weights of MATLAB's rgb2gray); scaled to [0, 1];
  * ground truth used in the experiments: the simplified 2-4 class maps shown in
    the paper's Fig. 22, re-created by tools/extract_bsds_gt_from_figure.py and
    stored in data/bsds_gt/ (`paper_ground_truth`); K = number of classes
    (100007: 2, 118035: 3, 167062: 3, 201080: 3, 241004: 4, 42049: 2, 67079: 2,
    86016: 2). Each map agrees with a merged human segmentation of BSDS500 on
    93.5-99.7 % of the pixels (merging = majority vote of each human region);
  * the raw human segmentations (3-51 regions) are still available
    (`ground_truths`, `select_ground_truth`).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import scipy.io as sio

ROOT = Path(__file__).resolve().parents[2] / "data" / "raw" / "BSR" / "BSDS500" / "data"
PAPER_GT_DIR = Path(__file__).resolve().parents[2] / "data" / "bsds_gt"
PAPER_IDS = ("100007", "118035", "167062", "201080", "241004", "42049", "67079", "86016")
SPLITS = ("train", "val", "test")
BT601 = np.array([0.2989, 0.5870, 0.1140])  # R, G, B weights


@dataclass(frozen=True)
class BSDSImage:
    image_id: str
    split: str
    rgb: np.ndarray                  # uint8, (H, W, 3)
    gray: np.ndarray                 # float64 in [0, 1], (H, W)
    ground_truths: list[np.ndarray]  # int64 label maps, values 0..R-1, one per annotator


def _find(image_id: str, root: Path) -> str:
    for split in SPLITS:
        if (root / "images" / split / f"{image_id}.jpg").exists():
            return split
    raise FileNotFoundError(f"BSDS500 image {image_id} not found under {root} (see data/README.md)")


def to_gray(rgb: np.ndarray) -> np.ndarray:
    """uint8 RGB -> float gray in [0, 1] with BT.601 weights."""
    return (rgb.astype(np.float64) @ BT601) / 255.0


def load(image_id: str, root: Path = ROOT) -> BSDSImage:
    split = _find(image_id, root)
    bgr = cv2.imread(str(root / "images" / split / f"{image_id}.jpg"), cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    mat = sio.loadmat(str(root / "groundTruth" / split / f"{image_id}.mat"))
    cells = mat["groundTruth"][0]
    # MATLAB labels start at 1 -> shift to 0
    gts = [cell["Segmentation"][0, 0].astype(np.int64) - 1 for cell in cells]
    return BSDSImage(image_id, split, rgb, to_gray(rgb), gts)


def paper_ground_truth(image_id: str, gt_dir: Path = PAPER_GT_DIR) -> tuple[np.ndarray, int]:
    """Simplified ground truth of the paper's Fig. 22 (labels 0..K-1) and its K."""
    lab = cv2.imread(str(gt_dir / f"{image_id}_gt.png"), cv2.IMREAD_GRAYSCALE)
    if lab is None:
        raise FileNotFoundError(gt_dir / f"{image_id}_gt.png")
    lab = lab.astype(np.int64)
    return lab, int(lab.max()) + 1


def select_ground_truth(img: BSDSImage, policy: str = "fewest") -> np.ndarray:
    """Pick one human segmentation: 'fewest' regions, 'most' regions, or 'first'."""
    if policy == "first":
        return img.ground_truths[0]
    counts = [len(np.unique(g)) for g in img.ground_truths]
    if policy == "fewest":
        return img.ground_truths[int(np.argmin(counts))]
    if policy == "most":
        return img.ground_truths[int(np.argmax(counts))]
    raise ValueError(f"unknown policy {policy!r}")


if __name__ == "__main__":  # quick check: python -m src.data.bsds500
    for pid in PAPER_IDS:
        im = load(pid)
        regions = [len(np.unique(g)) for g in im.ground_truths]
        print(f"{pid} ({im.split}): {im.gray.shape}, annotations={len(regions)}, regions={regions}")
