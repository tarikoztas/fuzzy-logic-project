# CP5 — Experimental Results

All numbers are generated from `results/tables/*.csv` by `report/make_cp5.py` (same computation as the report). 10 seeds per setting; paired two-sided Wilcoxon tests over seeds.

## 1. Reproduction (E1–E4)
- FCM vs paper-reported FCM: mean |Δ| ACC 0.63 points (max 1.85).
- Proposed method vs paper-reported: 0.11 ACC points up to 5 % noise, 3.02 at 10–15 % (largest gap 8.2).
- Ablation (Table 1): all components 99.91 / 99.24 / 99.22 % (sy1/sy2/sy3); non-local alone 97.5–99.6 %; local alone 97.5–99.9 %.
- Sensitivity: At 5 % noise the method is insensitive to σ, w and δ (Fig. 4): over σ ∈ [0.05, 0.9], w ∈ {3, 5, 7, 9} and δ ∈ [0, 0.8] the ACC of each image varies by at most 0.35, 0.17 and 0.02 points. Unlike Fig. 10 of [1], the ACC does not decrease above σ = 0.4; on sy3 it increases slightly up to σ = 0.9 (99.22 → 99.39 %), consistent with Section VIII-E. For k ≥ 5 the ACC is stable (range 0.03 points), while k = 1 degrades it (sy3: 95.94 %), in line with the paper's statement that k should exceed 5. The sparsity factor mainly controls convergence: on sy3 the iterations fall from 15.9 without sparsity (δ = 0) to a minimum of 11.1 at δ = 0.2 and rise again for larger δ (12.7 at the paper's δ = 0.4).

## 2. Single-factor ablation of the paper's choices (C2)
Table V changes one choice at a time. The reward factor has the largest effect: with σ = 0.9 the ACC at 15 % noise rises from 92.38 to 96.88 % on sy2 and from 89.13 to 94.88 % on sy3; the gap to the paper-reported values shrinks from 6.1/8.2 to 1.7/2.5 points and the iterations at 15 % fall from 27.1 to 17.6. The golden ratio is not special: ρ = 0.5 gives the same or slightly higher ACC, whereas 0.7 and 0.8 are worse at high noise, and the rounding of the reward-set size hardly matters. The absolute difference in Eqs. 15–16 is better than the printed signed one at 15 % (sy3: 91.59 vs 89.13 %). Making empty columns crisp (argmax) forces V_PC = 100 % and costs ACC on sy2 at 5 % (96.11 vs 99.24 %), and running the non-local means on 0–255 intensities is clearly worse at 15 % (sy3: 80.05 %).

## 3. Proposed extension (E5) — CP4 hypotheses
**Extension (E5, synthetic images): ACC (%) mean ± std over 10 seeds; Δ vs ASRFCM with the paper's coefficients, * = paired Wilcoxon p < 0.05.**

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
| Time per 256x256 image (s, E7) | 1.20 | 2.95 | +1.75 | 2.67 | +1.47 |

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

- **H1 rejected**: the pre-registered FIS is worse at 10–15 % (by 15.5–16.0 points at 15 % on sy2/sy3); the exploratory split variant loses 3.8–5.2 points at 15 %. Significant gains: FIS-full on sy2 at 1 % (+0.35); FIS-split on sy2 at 1 % (+0.32); FIS-split on sy2 at 5 % (+0.15).
- **H3 holds** for shape/bisector/Sugeno (≤ 0.54 points for full, ≤ 0.43 for split); mean of maxima is the exception (+2.94 points for full at 15 %).
- **H4 holds**: Sugeno within 0.43 points of Mamdani-centroid.

## 4. Robustness per noise type (C1)
Fig. 6 separates the components of the mixed noise (values: mean over sy1–sy3, FCM → reproduced method at 20 %). Salt-and-pepper (88.3 → 99.3 %) and speckle noise (88.1 → 99.4 %) are almost completely removed: impulses sit at the ends of the sorted neighbourhood and fall into the penalty set, and speckle leaves dark regions untouched. Gaussian noise is harder (70.1 → 97.3 %), and the combination is clearly the hardest case (60.8 → 86.9 %): the method copes well with each component alone but not with their sum at the same parameter. On noise-free images the method is slightly below FCM (99.9 vs 100.0 %) because the spatial terms smooth thin structures; the pre-registered FIS, which trusts consistent pixels, keeps 100.0 % there and is also better at 1 % noise (e.g. Gaussian: 100.0 vs 99.9 %). This is the regime the rule base was designed for; with more noise its trust in the pixel becomes a liability (Gaussian 20 %: 88.1 %). The split variant is equal to or slightly better than the paper's coefficients for impulse and speckle noise up to 10 % (salt-and-pepper 10 %: 99.8 vs 99.8 %) and falls behind for Gaussian and mixed noise at high density.

## 5. Real images (E6)
On the eight BSDS500 images (gray-level protocol, Table IX) the reproduced method raises the mean ACC of FCM from 57.87 to 79.85 % (paper-reported: 69.28 → 87.36 %). Our FCM is lower than the paper's because the paper clustered the color images (Section IX). H2 is rejected: the fuzzy-rule variants do not raise the mean ACC (full 72.04 %, split 78.70 %). For the colour re-run we use the minimal multichannel generalization of D-043 (ξ and ϑ per channel, Euclidean distances in RGB, one α, β, γ per pixel from channel-averaged differences; noise added to each channel). On the colour images, our FCM matches the paper-reported FCM within two points on 7 of 8 images (mean 68.38 vs 69.28 %), and the reproduced method reaches 85.29 % (paper-reported 87.36 %); the FIS variants give 82.25 (full) and 84.84 % (split).

## 6. Run time (E7)
On a 256×256 image FCM takes 0.17 s and the reproduced method 1.20 s, of which 1.01 s are spent on ξ and ϑ (Table XI); the sparse clustering itself is fast because it converges in few iterations. The Mamdani FIS adds 1.64 s (nine rules evaluated on a 201-point output grid for every pixel); the zero-order Sugeno variant avoids this grid.

## 7. Why the extension did not help
The pre-registered rule base gives the noisy pixel about 30 % of the total trust (paper formula: about 0.1 %), so noise leaks into the clustering; restricting the FIS to the split between ξ and ϑ removes the leak, but the input Dis = |ξ − ϑ| measures the noise of ξ rather than edges at high noise. The rule base was not tuned further on the test data (D-041).
