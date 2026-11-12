# Data

Large/raw data is not committed (`.gitignore`). This file documents sources and preparation so that the experiments can be reproduced.

## Synthetic images (sy1, sy2, sy3) — committed, `data/synthetic/`

`sy{1,2,3}_labels.png` are 256×256 label maps (pixel value = class index 0..K−1). `src/data/synthetic.py` turns them into the clean gray image and the ground truth.

- They were **re-created from Fig. 9 of the reference paper** (Wu et al. 2024), because the paper does not publish its images: the embedded raster of Fig. 9 was cropped per panel, resized to 256×256, every pixel was assigned to the nearest gray level read from the figure, and a 5×5 median filter removed JPEG ringing. Script: `tools/extract_synthetic_from_figure.py` (needs the publisher PDF, which is not in git, and `pymupdf`).
- Gray levels (0–255) measured in the figure: sy1 {0, 255} (K=2), sy2 {0, 107, 255} (K=3), sy3 {0, 107, 222} (K=3).
- Same shapes and levels as the paper, but **not the authors' original files** (resolution and edge pixels differ).

## BSDS500 — not committed, `data/raw/`

- Source: Berkeley Segmentation Data Set and Benchmark 500, P. Arbeláez, M. Maire, C. Fowlkes, J. Malik, "Contour detection and hierarchical image segmentation," IEEE TPAMI 33(5), 2011, doi:10.1109/TPAMI.2010.161.
- Archive: <https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/grouping/BSR/BSR_bsds500.tgz> (downloaded 2026-11-11; SHA-256 `97e49d31764f3912f0c4122707d53062ac9e783ba0f095e447a4d53c1a41af8e`).
- Preparation:
  ```bash
  mkdir -p data/raw/dl
  curl -L -o data/raw/dl/BSR_bsds500.tgz https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/grouping/BSR/BSR_bsds500.tgz
  tar -xzf data/raw/dl/BSR_bsds500.tgz -C data/raw BSR/BSDS500/data
  python -m src.data.bsds500     # lists the 8 paper images and their annotations
  ```
- Images used in the paper: 100007, 118035, 167062, 201080, 241004, 42049, 67079, 86016 (321×481).
- Color → gray: BT.601 weights (0.2989 R + 0.5870 G + 0.1140 B). Ground truth: each image has 5–6 human segmentations; `select_ground_truth(policy="fewest")` picks the one with the fewest regions. The final protocol (and K per image) is decided in experiment E6 (decision D-029).

## Noise

Generated on the fly with fixed seeds (`src/data/noise.py`). "p % mixed noise" = Gaussian (variance p) → speckle (variance p) → salt-and-pepper (density p); see `report/decisions.md` D-027 and the plausibility check `experiments/noise_check/check_noise_levels.py`.
