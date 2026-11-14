# Adaptive Sparse Regularized Fuzzy Clustering for Noisy Image Segmentation — Reproduction and a Fuzzy-Rule Extension

> Fuzzy Logic course term project. Report: [`report/report.pdf`](report/report.pdf) · Slides: [`presentation/presentation.pdf`](presentation/presentation.pdf) · Decisions and deviations from the paper: [`report/decisions.md`](report/decisions.md) · Checkpoint notes: [`report/checkpoints/`](report/checkpoints/)

## Project Title

Reproduction and extension of *"Adaptive sparse regularized fuzzy clustering noise image segmentation algorithm based on complementary spatial information"* (Wu et al., 2024): Fuzzy C-Means with local and wavelet-domain non-local spatial information and ℓ0 sparse regularization, extended with an explicit Mamdani fuzzy inference system for its per-pixel trust coefficients.

## Student Information

- **Name:** Tarık Öztaş
- **Student ID:** 1306230040
- **University / Department:** İstanbul Üniversitesi-Cerrahpaşa, Computer Engineering
- **Course:** Fuzzy Logic (Bulanık Mantık) — Term Project, 2026–2027 Fall

## Original Paper

J. Wu, X. Wang, Y. Liu, and C. Fang, "Adaptive sparse regularized fuzzy clustering noise image segmentation algorithm based on complementary spatial information," *Expert Systems With Applications*, vol. 256, Art. no. 124943, 2024, doi: [10.1016/j.eswa.2024.124943](https://doi.org/10.1016/j.eswa.2024.124943).

The paper PDF is not redistributed here (publisher copyright). All code in this repository was written from scratch for this project; no implementation by the authors was used (decision D-020).

## Problem Description

Image segmentation divides an image into homogeneous regions. Fuzzy C-Means (FCM) gives every pixel a degree of membership in each of K clusters, but it looks at each gray value in isolation and therefore breaks down under noise. The paper adds two corrected versions of every pixel — a local estimate built from golden-ratio reward/penalty sets of neighbours and a non-local estimate computed in the dual-tree complex wavelet domain — weighs the three values with per-pixel coefficients α, β, γ, and makes the membership matrix sparse with an ℓ0 penalty. The goal is robust segmentation under mixed Gaussian, salt-and-pepper and multiplicative noise with few iterations.

This project (1) re-implements FCM and the full method, (2) reproduces the paper's main synthetic experiments, ablation and BSDS500 experiment, (3) documents where the paper is ambiguous or inconsistent, and (4) replaces the paper's closed-form coefficient rule with an explicit, inspectable fuzzy rule base and evaluates it under controlled conditions.

## Method

| Step | Paper | Code |
|---|---|---|
| Baseline FCM | Alg. 1, Eqs. 1–3 | `src/fcm/baseline_fcm.py` |
| Local information ξ: neighbours sorted, the middle ⌊0.618·(N_R−1)⌋ form the reward set (weight 1+σ), the rest the penalty set (1−σ); gray and spatial similarity | Alg. 2, Eqs. 5–9 | `src/fcm/local_info.py` |
| Non-local information ϑ: one-level DTCWT (1 low-pass + 6 complex sub-bands), non-local means on each, inverse DTCWT | Eqs. 10–11 | `src/fcm/nonlocal_wavelet.py` |
| Adaptive coefficients α = 1/(ΔG1+ΔG2), β = ΔG1, γ = ΔG2 with ΔG = k·exp(y − ξ) | Eqs. 13–19 | `src/fcm/adaptive_params.py` |
| Sparse-regularised FCM: centres → η → hard threshold √δ → normalise | Alg. 3, Eqs. 20–29 | `src/fcm/sparse_fcm.py`, `src/fcm/pipeline.py` |
| **Extension:** α, β, γ from a Mamdani fuzzy inference system | — (ours) | `src/fuzzy/`, `src/fcm/fis_coefficients.py` |

Parameters (paper): w = 5, S = 15, υ = 4, g = 10, σ = 0.3, k = 15, δ = 0.4, m = 2, ε = 10⁻⁶, T = 100.

## Fuzzy System Architecture

![architecture](results/figures/architecture.png)

**Fuzzy clustering part (paper).**

| Element | Realisation |
|---|---|
| Inputs | noisy gray image y ∈ [0, 1]; derived features ξ (local) and ϑ (non-local); number of clusters K |
| Fuzzy sets / membership functions | one fuzzy set per cluster; membership u_ij ∈ [0, 1] of pixel j in cluster i (Eq. 2 / 28), columns sum to 1; Gaussian similarity kernels inside ξ and ϑ |
| "Inference" | minimisation of the objective (Eq. 12 / 20): a pixel close to centre c_i in the weighted distance d_ij gets a high membership in cluster i |
| Defuzzification | label_j = argmax_i u_ij |
| Outputs | membership matrix U, cluster centres, label map |

**Mamdani fuzzy inference system (extension, `src/fuzzy/`, `src/fcm/fis_coefficients.py`).**

| Element | Realisation |
|---|---|
| Inputs | Dev = \|y − (ξ+ϑ)/2\| (pixel vs. consensus of the two estimates), Dis = \|ξ − ϑ\| (disagreement of the estimates) |
| Membership functions | Small / Medium / Large on [0, 1]; triangular/trapezoidal (default) or Gaussian |
| Rule base | 9 rules, e.g. *IF Dev is Large AND Dis is Small THEN α is Low, β is High, γ is High* (full table: `results/tables/fis_rule_base.csv`) |
| Inference | AND = min, implication = min, aggregation = max (Mamdani); zero-order Sugeno variant |
| Defuzzification | centroid (default), bisector, mean of maxima |
| Outputs | α, β, γ per pixel → used by the sparse FCM |

![membership functions](results/figures/fis_membership.png)
![inference example](results/figures/fis_inference_example.png)

## Dataset

- **Synthetic images sy1, sy2, sy3** (256×256, K = 2, 3, 3): label maps re-created from the paper's Fig. 9 (`data/synthetic/`, `tools/extract_synthetic_from_figure.py`); same shapes and gray levels, not the authors' files.
- **BSDS500** — the 8 images used in the paper (100007, 118035, 167062, 201080, 241004, 42049, 67079, 86016): images from the official archive (not committed; download steps in [`data/README.md`](data/README.md)); ground truths = the simplified 2–4 class maps of the paper's Fig. 22, re-created from the figure (`data/bsds_gt/`) and validated against the human segmentations (93.5–99.7 % agreement).
- **Noise** (`src/data/noise.py`, seeded): "p % mixed noise" = Gaussian (variance p) → speckle (variance p) → salt-and-pepper (density p); also each type alone.

## Installation

```bash
git clone https://github.com/tarikoztas/fuzzy-logic-project.git
cd fuzzy-logic-project
python -m venv .venv                 # Python 3.12 tested
# Windows: .venv\Scripts\activate    Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt      # or requirements.lock.txt for the exact versions
```
BSDS500 (only for the real-image experiments): see [`data/README.md`](data/README.md).

## Requirements

Python 3.12 (Windows 11 tested), `numpy<2` (required by `dtcwt 0.13`, which still calls `np.asfarray`), scipy, scikit-image, opencv-python, matplotlib, pandas, scikit-learn (tests only), dtcwt, PyYAML. Ranges in `requirements.txt`, exact versions in `requirements.lock.txt`. No GPU and no internet access are needed after installation.

## How to Run

```bash
python -m pytest                                                                     # unit tests
python experiments/baseline/run_baseline.py --config experiments/baseline/config.yaml   # E1: FCM
python experiments/proposed/run_proposed.py --config experiments/proposed/config.yaml   # E2: paper's method
python experiments/ablation/run_ablation.py --config experiments/ablation/config.yaml   # E3: Table 1 ablation
python experiments/run_grid.py --config experiments/contribution/main.yaml           # E5: FIS extension
python experiments/run_grid.py --config experiments/contribution/bsds.yaml           # E6: BSDS500
python experiments/run_grid.py --config experiments/contribution/fis_variants.yaml   # E5: MF / defuzzification / Sugeno
python experiments/run_grid.py --config experiments/contribution/robustness.yaml     # E5: noise types (C1)
python experiments/run_grid.py --config experiments/contribution/ablation_c2.yaml    # E5: single-factor ablation (C2)
python experiments/run_grid.py --config experiments/sensitivity/config.yaml          # E4: sigma, w, k, delta
python experiments/run_grid.py --config experiments/contribution/tuning.yaml            # E8: tuning (seeds 100-104 only)
python experiments/summarize_tuning.py                                                     # E8: tuning log + selection rule
python experiments/run_grid.py --config experiments/contribution/second_iteration.yaml  # E8: test (seeds 0-9)
python experiments/run_grid.py --config experiments/contribution/bsds_second.yaml       # E8: BSDS500 gray
python experiments/run_grid.py --config experiments/contribution/bsds_rgb_second.yaml   # E8: BSDS500 colour
python experiments/run_grid.py --config experiments/contribution/robustness_second.yaml # E8: noise types
python experiments/timing/run_timing.py                                              # E7: run time (idle machine)
python experiments/analyze_contribution.py      # summaries, Wilcoxon tests, figures
python experiments/analyze_second_iteration.py  # E8: hypotheses H5/H6, Wilcoxon tests, figures
python experiments/plot_reproduction.py         # E1-E3 figures
python experiments/plot_panels.py               # segmentation panels
python report/build_report.py                   # report.html -> report.pdf (headless Edge/Chrome)
python report/build_report.py --lang tr         # Turkish report: report_tr.pdf
python presentation/build_slides.py             # presentation.pdf + .pptx (add --lang tr for the Turkish slides)
python demo/demo.py --image sy3 --noise mixed --level 10 --pixel 120 80   # live demo
```
Results go to `results/tables/*.csv` and `results/figures/*`. `run_grid.py` uses all CPU cores but one and can be resumed.

## Reproduction Experiments

| ID | Paper | What is compared | Output |
|---|---|---|---|
| E1 | Tables 2–8 (FCM column) | our FCM vs paper-reported FCM, sy1–sy3 × {1, 5, 10, 15} % × 10 seeds | `e1_fcm_vs_paper.csv`, `e1_fcm_vs_paper.png` |
| E2 | Tables 2–8 ("Ours" column) | our ASRFCM-CSI vs paper-reported | `e2_asrfcm_vs_paper.csv`, `e2_asrfcm_vs_paper.png` |
| E3 | Table 1 | component ablation, 5 % noise | `e3_ablation_vs_paper.csv`, `e3_ablation.png` |
| E4 | Figs. 10–13 | sensitivity to σ, w, k, δ | `e4_sensitivity_summary.csv`, `e4_sensitivity_*.png` |
| E6 | Table 9 | 8 BSDS500 images, 5 % noise | `e6_bsds_summary.csv`, `panel_bsds.png` |

<!-- BEGIN:reproduction -->
**E1/E2 — ACC (%) on the synthetic images, ours (mean of 10 seeds) vs paper-reported:**

| Image | Noise % | FCM ours | FCM paper | ASRFCM ours | ASRFCM paper |
|---|---|---|---|---|---|
| sy1 | 1 | 99.50 | 99.49 | 99.99 | 99.89 |
| sy1 | 5 | 95.24 | 95.20 | 99.91 | 99.86 |
| sy1 | 10 | 85.95 | 86.18 | 99.72 | 99.75 |
| sy1 | 15 | 77.56 | 77.97 | 99.34 | 99.56 |
| sy2 | 1 | 97.52 | 97.82 | 99.58 | 99.43 |
| sy2 | 5 | 77.14 | 77.16 | 99.24 | 99.22 |
| sy2 | 10 | 67.22 | 67.75 | 97.82 | 99.04 |
| sy2 | 15 | 61.89 | 62.68 | 92.38 | 98.53 |
| sy3 | 1 | 96.22 | 95.87 | 99.95 | 99.84 |
| sy3 | 5 | 72.90 | 74.75 | 99.22 | 99.43 |
| sy3 | 10 | 61.42 | 62.61 | 96.62 | 98.91 |
| sy3 | 15 | 55.66 | 57.45 | 89.13 | 97.36 |

Mean |ours − paper| ACC: FCM 0.63 points; ASRFCM 0.11 points up to 5 % noise and 3.02 points at 10–15 %. Figures: `results/figures/e1_fcm_vs_paper.png`, `e2_asrfcm_vs_paper.png`.
<!-- END:reproduction -->

## Proposed Extension

**What:** the closed-form rule for the per-pixel trust coefficients (Eqs. 13–19) is replaced by a Mamdani fuzzy inference system with two inputs (Dev, Dis), nine IF–THEN rules and centroid defuzzification. A post-hoc variant (*split*, labelled exploratory) keeps the paper's α and total trust and lets the FIS only split the trust between ξ and ϑ.

**Why:** with the paper's parameters α ≈ 0.01–0.1 and β ≈ γ for almost every pixel, so the two corrected images are always weighted equally; our reproduction shows that they fail in different places (the non-local estimate is nearly a 15×15 mean filter and blurs edges; the local estimate is edge-aware but weaker under heavy noise). An explicit rule base can express this and is inspectable.

**How it was evaluated:** hypotheses and success criteria were fixed before the experiments ([CP4](report/checkpoints/CP4_contribution_proposal.md)); same images, noise realisations, seeds and initial memberships for all methods; 10 seeds; paired Wilcoxon signed-rank tests. Variants: membership-function shape, defuzzification method, Mamdani vs Sugeno; robustness per noise type and density (C1); single-factor ablation of the paper's arbitrary choices (C2).

**Result of the first iteration:** the pre-registered rule base did not beat the paper's formula (H1 and H2 rejected; H3 and H4 hold). The analysis found two causes: the rule base leaves the noisy pixel ~30 % of the trust (paper ~0.1 %), and its inputs cannot separate edges from noise at high density; the ablation showed that the reward factor σ dominates the high-noise behaviour.

**Second iteration (pre-registered, [CP6](report/checkpoints/CP6_second_iteration_plan.md), D-044/D-045):** three candidates aimed at these causes — (A) the same rule base with α bounded to the paper's range, (B) an impulse input |y − median3×3(y)|, (C) a three-rule Mamdani system that maps an image-level noise estimate (median(|HH|)/0.6745 of the Haar transform) to the reward factor σ (`src/fcm/fis_sigma.py`). They were tuned only on seeds 100–104 (9 of 12 allowed configurations, all in `results/tables/e8_tuning_log.csv`); the selection rule, the chosen variants (FIS-σ and the secondary FIS-σ+A) and the hypotheses H5/H6 were committed before the single test run on seeds 0–9. A fixed σ = 0.9 is used as a control to separate the value of the rule from the value of a larger σ.

## Experimental Results

<!-- BEGIN:results -->
**Extension, first iteration (E5, synthetic images): ACC (%) mean ± std over 10 seeds; Δ vs ASRFCM with the paper's coefficients, * = paired Wilcoxon p < 0.05.**

| Image | Noise % | FCM | ASRFCM (paper coeff.) | +FIS full | +FIS split | Δ full | Δ split |
|---|---|---|---|---|---|---|---|
| sy1 | 1 | 99.50 ± 0.03 | 99.99 ± 0.00 | 99.99 ± 0.00 | 99.99 ± 0.00 | +0.00 | +0.00 |
| sy1 | 5 | 95.24 ± 0.09 | 99.91 ± 0.02 | 99.88 ± 0.02 | 99.91 ± 0.02 | -0.03* | +0.00 |
| sy1 | 10 | 85.95 ± 0.17 | 99.72 ± 0.03 | 99.43 ± 0.03 | 99.66 ± 0.03 | -0.28* | -0.05* |
| sy1 | 15 | 77.56 ± 0.17 | 99.34 ± 0.04 | 97.57 ± 0.11 | 98.76 ± 0.07 | -1.77* | -0.58* |
| sy2 | 1 | 97.52 ± 0.06 | 99.58 ± 0.02 | 99.92 ± 0.01 | 99.90 ± 0.01 | +0.35* | +0.32* |
| sy2 | 5 | 77.14 ± 0.21 | 99.24 ± 0.04 | 98.29 ± 0.06 | 99.38 ± 0.04 | -0.95* | +0.15* |
| sy2 | 10 | 67.22 ± 0.22 | 97.82 ± 0.09 | 87.59 ± 0.37 | 96.25 ± 0.10 | -10.23* | -1.57* |
| sy2 | 15 | 61.89 ± 0.18 | 92.38 ± 0.19 | 76.37 ± 0.25 | 88.63 ± 0.23 | -16.01* | -3.75* |
| sy3 | 1 | 96.22 ± 0.06 | 99.95 ± 0.01 | 99.90 ± 0.01 | 99.96 ± 0.01 | -0.05* | +0.00 |
| sy3 | 5 | 72.90 ± 0.17 | 99.22 ± 0.04 | 97.41 ± 0.05 | 99.11 ± 0.05 | -1.81* | -0.11* |
| sy3 | 10 | 61.42 ± 0.23 | 96.62 ± 0.12 | 86.24 ± 0.34 | 94.13 ± 0.17 | -10.37* | -2.48* |
| sy3 | 15 | 55.66 ± 0.21 | 89.13 ± 0.35 | 73.59 ± 0.45 | 83.94 ± 0.39 | -15.54* | -5.19* |

**Guideline-format table (all synthetic settings):**

| Metric | Baseline (ASRFCM-paper) | Improved (FIS-full) | Change (FIS-full) | Improved (FIS-split) | Change (FIS-split) |
|---|---|---|---|---|---|
| ACC | 97.74 ± 3.33 | 93.02 ± 9.27 | -4.73 | 96.64 ± 5.02 | -1.11 |
| F | 97.40 ± 3.76 | 92.05 ± 10.55 | -5.35 | 96.00 ± 5.94 | -1.40 |
| NMI | 90.32 ± 11.35 | 79.45 ± 22.06 | -10.87 | 87.29 ± 15.29 | -3.03 |
| Kappa (Cohen) | 95.98 ± 5.72 | 87.95 ± 15.69 | -8.03 | 94.05 ± 8.61 | -1.93 |
| Kappa (paper's definition) | 94.94 ± 7.51 | 84.35 ± 20.88 | -10.59 | 92.46 ± 11.32 | -2.48 |
| V_PC | 97.75 ± 3.06 | 94.85 ± 5.55 | -2.90 | 97.83 ± 2.77 | +0.08 |
| V_PE | 3.61 ± 4.96 | 8.30 ± 9.05 | +4.69 | 3.46 ± 4.46 | -0.15 |
| Iterations | 16.38 ± 9.76 | 22.13 ± 15.73 | +5.76 | 17.51 ± 11.29 | +1.13 |
| Time per 256x256 image (s, E7) | 0.79 | 2.08 | +1.30 | 2.10 | +1.31 |

**Real images (E6): BSDS500, 5 % mixed noise, ACC (%) mean of 10 seeds, gray and colour (RGB) protocols; paper values from its Table 9:**

| Image | K | FCM | ASRFCM | +FIS full | +FIS split | FCM (RGB) | ASRFCM (RGB) | +FIS full (RGB) | +FIS split (RGB) | FCM paper | ASRFCM paper |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 100007 | 2 | 57.82 | 79.86 | 77.98 | 79.71 | 65.92 | 80.69 | 81.11 | 80.88 | 65.96 | 80.83 |
| 118035 | 3 | 54.77 | 84.70 | 72.30 | 83.24 | 72.09 | 93.92 | 92.56 | 93.72 | 73.08 | 96.24 |
| 167062 | 3 | 77.14 | 98.02 | 80.07 | 93.61 | 79.18 | 95.09 | 75.61 | 92.34 | 78.86 | 98.87 |
| 201080 | 3 | 42.27 | 54.06 | 49.18 | 54.49 | 62.07 | 83.74 | 82.85 | 83.65 | 62.72 | 85.12 |
| 241004 | 4 | 44.80 | 72.82 | 63.96 | 72.12 | 59.82 | 73.32 | 76.67 | 73.43 | 60.36 | 73.16 |
| 42049 | 2 | 67.96 | 90.49 | 89.18 | 90.27 | 77.71 | 91.62 | 91.25 | 91.58 | 81.67 | 96.36 |
| 67079 | 2 | 60.52 | 80.81 | 76.15 | 79.83 | 68.02 | 82.94 | 80.78 | 82.59 | 68.67 | 85.06 |
| 86016 | 2 | 57.64 | 78.06 | 67.51 | 76.34 | 62.21 | 80.99 | 77.14 | 80.54 | 62.89 | 83.26 |
| mean |  | 57.87 | 79.85 | 72.04 | 78.70 | 68.38 | 85.29 | 82.25 | 84.84 | 69.28 | 87.36 |

More results: robustness per noise type `results/figures/e5_robustness_acc.png`, single-factor ablation `results/tables/e5_ablation_c2_summary.csv`, FIS variants `results/tables/e5_fis_variants_summary.csv`, sensitivity `results/figures/e4_sensitivity_acc.png`, run time `results/tables/e7_timing_summary.csv`, segmentations `results/figures/panel_synthetic.png`, `results/figures/panel_bsds.png`. Full discussion: [`report/report.pdf`](report/report.pdf).
<!-- END:results -->

<!-- BEGIN:second_iteration -->
**Second iteration (E8, pre-registered in `report/checkpoints/CP6_second_iteration_plan.md`): ACC (%) on the synthetic test grid, mean ± std over seeds 0–9; Δ vs ASRFCM with the paper's settings, * = paired Wilcoxon p < 0.05.**

| Image | Noise % | ASRFCM (σ = 0.3) | σ = 0.9 fixed | FIS-σ (Δ) | FIS-σ+A (Δ) |
|---|---|---|---|---|---|
| sy1 | 1 | 99.99 ± 0.00 | 99.99 ± 0.00 | 99.99 (+0.00) | 99.99 (+0.00) |
| sy1 | 5 | 99.91 ± 0.02 | 99.92 ± 0.01 | 99.92 (+0.01*) | 99.92 (+0.01*) |
| sy1 | 10 | 99.72 ± 0.03 | 99.77 ± 0.02 | 99.77 (+0.06*) | 99.77 (+0.05*) |
| sy1 | 15 | 99.34 ± 0.04 | 99.54 ± 0.03 | 99.55 (+0.21*) | 99.48 (+0.13*) |
| sy2 | 1 | 99.58 ± 0.02 | 99.51 ± 0.01 | 99.57 (-0.01*) | 99.89 (+0.31*) |
| sy2 | 5 | 99.24 ± 0.04 | 99.23 ± 0.03 | 99.25 (+0.01) | 99.47 (+0.23*) |
| sy2 | 10 | 97.82 ± 0.09 | 98.77 ± 0.06 | 98.77 (+0.95*) | 98.54 (+0.71*) |
| sy2 | 15 | 92.38 ± 0.19 | 96.88 ± 0.07 | 97.00 (+4.61*) | 95.47 (+3.08*) |
| sy3 | 1 | 99.95 ± 0.01 | 99.96 ± 0.01 | 99.96 (+0.00*) | 99.96 (+0.00*) |
| sy3 | 5 | 99.22 ± 0.04 | 99.39 ± 0.05 | 99.37 (+0.15*) | 99.37 (+0.15*) |
| sy3 | 10 | 96.62 ± 0.12 | 98.34 ± 0.08 | 98.38 (+1.76*) | 97.76 (+1.14*) |
| sy3 | 15 | 89.13 ± 0.35 | 94.88 ± 0.18 | 95.08 (+5.95*) | 92.94 (+3.81*) |

H5 (FIS-σ better than the paper at 10/15 % without loss at 1/5 %) holds; H6 (FIS-σ+A never below the paper) holds; as expected, FIS-σ is practically equal to a fixed σ = 0.9 on this grid (differences -0.02 … +0.19 points). Tuning log: `results/tables/e8_tuning_log.csv`; hypotheses: `results/tables/e8_hypotheses.csv`; figures `results/figures/e8_*.png`.

**Guideline-format table (second iteration):**

| Metric | Baseline (ASRFCM-paper) | Improved (FIS-σ) | Change (FIS-σ) | Improved (FIS-σ+A) | Change (FIS-σ+A) |
|---|---|---|---|---|---|
| ACC | 97.74 ± 3.33 | 98.88 ± 1.41 | +1.14 | 98.55 ± 2.11 | +0.80 |
| F | 97.40 ± 3.76 | 98.67 ± 1.62 | +1.27 | 98.23 ± 2.54 | +0.83 |
| NMI | 90.32 ± 11.35 | 94.04 ± 5.90 | +3.72 | 92.97 ± 8.16 | +2.64 |
| Kappa (Cohen) | 95.98 ± 5.72 | 97.99 ± 2.39 | +2.01 | 97.41 ± 3.60 | +1.43 |
| Kappa (paper's definition) | 94.94 ± 7.51 | 97.50 ± 3.18 | +2.56 | 96.75 ± 4.75 | +1.81 |
| V_PC | 97.75 ± 3.06 | 98.81 ± 1.50 | +1.05 | 98.80 ± 1.56 | +1.05 |
| V_PE | 3.61 ± 4.96 | 1.91 ± 2.42 | -1.70 | 1.91 ± 2.51 | -1.71 |
| Iterations | 16.38 ± 9.76 | 13.28 ± 4.84 | -3.10 | 12.89 ± 4.82 | -3.48 |
| Time per 256x256 image (s, E7) | 0.79 | 0.93 | +0.15 | 1.95 | +1.17 |
<!-- END:second_iteration -->

## Limitations

- The synthetic images and the BSDS500 ground truths were re-created from the paper's figures; the noise model is our reading of an under-specified description. Remaining differences to the paper are discussed in the report.
- K must be given in advance (as in the paper).
- The first fuzzy rule base was designed from an analysis of the synthetic images; it did not generalise to high noise and was not tuned further on the test data.
- The second iteration was tuned on other noise realisations of the same synthetic images, and its ideas came from observations on the test seeds; on mixed noise its gain equals that of a fixed σ = 0.9, and its image-level noise estimate counts texture as noise.
- The method is described for gray values; colour images are handled by our minimal multichannel generalisation (D-043). The paper's further datasets (AID, MSRC, NASA, COCO; Table 10) were not used.
- Run times were measured on one laptop CPU with our Python implementation and are not comparable to the paper's MATLAB timings.

## References

Full verified list (IEEE format, DOIs checked on Crossref): [`references/README.md`](references/README.md). Main sources: Wu et al. 2024 (reference paper); Bezdek et al. 1984 (FCM); Kingsbury 2001 (DTCWT); Buades et al. 2008 (non-local means); Arbeláez et al. 2011 (BSDS500); Zadeh 1965; Mamdani & Assilian 1975; Takagi & Sugeno 1985; Wang et al. 2021 (SRFCM).
