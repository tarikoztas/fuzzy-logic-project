"""Re-create the simplified ground truths of the 8 BSDS500 images from Fig. 22 of
Wu et al. (2024) (decision D-029).

The paper evaluates on BSDS500 with merged, 2-4 class ground truths shown in its
Fig. 22, not with the raw human segmentations (which have 3-51 regions). We
rebuild those label maps from the figure:
  1. take the embedded raster of Fig. 22 (4 rows x 4 panels: image, GT, image, GT);
  2. crop each GT panel (3-px margin), assign every pixel to the nearest palette
     colour (yellow, blue, navy, teal);
  3. resize to the BSDS size 321 x 481 (nearest neighbour) and apply a 5x5 median filter.
Classes are numbered in palette order among the colours present, so K = number
of colours in the panel. The result is committed (data/bsds_gt/*.png); this
script needs the publisher PDF (not in git) and PyMuPDF.

Usage:
    python tools/extract_bsds_gt_from_figure.py --pdf references/papers/Wu_2024_ASRFCM_ESWA.pdf
"""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

ORDER = ("100007", "118035", "167062", "201080", "241004", "42049", "67079", "86016")  # row-major in Fig. 22
ROWS = [(1, 245), (306, 551), (613, 857), (908, 1152)]
GT_COLS = [(385, 749), (1147, 1515)]
PALETTE = np.array([[245, 218, 135],   # yellow
                    [0, 114, 203],     # blue
                    [42, 14, 84],      # navy
                    [104, 172, 162]],  # teal
                   dtype=np.float64)
MARGIN = 3
SIZE = (481, 321)  # (width, height) for cv2


def load_figure(pdf: Path) -> np.ndarray:
    import pymupdf

    doc = pymupdf.open(pdf)
    for page in doc:
        if "Fig. 22." not in page.get_text():
            continue
        for info in page.get_images(full=True):
            pix = pymupdf.Pixmap(doc, info[0])
            if (pix.height, pix.width) != (1196, 1517):  # the Fig. 22 raster (other figures share the page)
                continue
            if pix.n != 3:
                pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
            return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[..., :3]
    raise ValueError("Fig. 22 raster (1517 x 1196) not found")


def panel_labels(fig: np.ndarray, r: tuple[int, int], c: tuple[int, int]) -> np.ndarray:
    crop = fig[r[0] + MARGIN : r[1] - MARGIN, c[0] + MARGIN : c[1] - MARGIN].astype(np.float64)
    d = ((crop[..., None, :] - PALETTE[None, None]) ** 2).sum(-1)
    lab = np.argmin(d, axis=-1).astype(np.uint8)
    # a colour is present only if enough pixels are (almost) exactly that colour;
    # anti-aliased edge pixels lie between two colours and must not create classes
    pure = d.min(axis=-1) < 25.0**2
    present = [k for k in range(len(PALETTE)) if ((lab == k) & pure).mean() > 0.003]
    remap = np.zeros(len(PALETTE), dtype=np.uint8)
    for new, old in enumerate(present):
        remap[old] = new
    # rare colours (anti-aliasing) go to the nearest present colour
    d_present = d[..., present]
    lab = np.array(present, dtype=np.uint8)[np.argmin(d_present, axis=-1)]
    lab = remap[lab]
    lab = cv2.resize(lab, SIZE, interpolation=cv2.INTER_NEAREST)
    return cv2.medianBlur(lab, 5)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pdf", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=Path("data/bsds_gt"))
    args = ap.parse_args()
    fig = load_figure(args.pdf)
    args.out.mkdir(parents=True, exist_ok=True)
    i = 0
    for r in ROWS:
        for c in GT_COLS:
            lab = panel_labels(fig, r, c)
            cv2.imwrite(str(args.out / f"{ORDER[i]}_gt.png"), lab)
            frac = np.bincount(lab.ravel()) / lab.size
            print(f"{ORDER[i]}: K={lab.max() + 1}, class fractions={np.round(frac, 3).tolist()}")
            i += 1


if __name__ == "__main__":
    main()
