"""Re-create the label maps of the synthetic images sy1, sy2, sy3 from Fig. 9 of
Wu et al. (2024), ESWA 256:124943.

The paper does not publish its synthetic images, so we rebuild them from the
figure. Steps:
  1. take the single embedded raster image of Fig. 9 (PDF page 9, three panels);
  2. crop each panel (a 3-px margin removes the thin frame drawn around panel a);
  3. resize to 256x256 (area interpolation);
  4. assign every pixel to the nearest of the gray levels read from the figure
     (sy1: 0/255, sy2: 0/107/255, sy3: 0/107/222);
  5. 5x5 median filter on the label map to remove JPEG ringing at the edges.

The result (`data/synthetic/sy{1,2,3}_labels.png`, values 0..K-1) is committed,
so this script is only needed to re-create those files. It needs the publisher
PDF (kept locally, not in git) and PyMuPDF (`pip install pymupdf`, not part of
requirements.txt because the experiments do not need it).

Usage:
    python tools/extract_synthetic_from_figure.py --pdf references/papers/Wu_2024_ASRFCM_ESWA.pdf
"""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

# Gray levels measured in the figure (most frequent values per panel).
LEVELS = {"sy1": [0, 255], "sy2": [0, 107, 255], "sy3": [0, 107, 222]}

# Panel boxes inside the embedded 1004x371 image: (row0, row1, col0, col1), end-exclusive.
# Found from the dark frame / dark background columns (rows 0..315).
PANELS = {"sy1": (0, 316, 0, 325), "sy2": (0, 316, 339, 664), "sy3": (0, 316, 679, 1004)}
MARGIN = 3
SIZE = 256


def load_figure(pdf_path: Path) -> np.ndarray:
    import pymupdf  # optional dependency, only for this tool

    doc = pymupdf.open(pdf_path)
    page = doc[8]  # page 9 (0-based index)
    xref = page.get_images(full=True)[0][0]
    pix = pymupdf.Pixmap(doc, xref)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if img.shape != (371, 1004, 1):
        raise ValueError(f"unexpected Fig. 9 raster shape {img.shape}")
    return img[..., 0]


def panel_to_labels(fig: np.ndarray, name: str) -> np.ndarray:
    r0, r1, c0, c1 = PANELS[name]
    crop = fig[r0 + MARGIN : r1 - MARGIN, c0 + MARGIN : c1 - MARGIN].astype(np.float32)
    small = cv2.resize(crop, (SIZE, SIZE), interpolation=cv2.INTER_AREA)
    levels = np.array(LEVELS[name], dtype=np.float32)
    labels = np.argmin(np.abs(small[..., None] - levels[None, None, :]), axis=2).astype(np.uint8)
    return cv2.medianBlur(labels, 5)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pdf", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=Path("data/synthetic"))
    args = ap.parse_args()

    fig = load_figure(args.pdf)
    args.out.mkdir(parents=True, exist_ok=True)
    for name in LEVELS:
        labels = panel_to_labels(fig, name)
        cv2.imwrite(str(args.out / f"{name}_labels.png"), labels)
        frac = np.bincount(labels.ravel(), minlength=len(LEVELS[name])) / labels.size
        print(f"{name}: K={len(LEVELS[name])}, class fractions={np.round(frac, 3).tolist()}")


if __name__ == "__main__":
    main()
