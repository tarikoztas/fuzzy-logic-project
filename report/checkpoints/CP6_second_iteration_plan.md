# CP6 — Second Iteration of the Contribution (protocol and pre-registration)

*Part 1 was committed before any tuning run; Part 2 (selected variant and hypothesis H5) is committed before the single test run. Results are reported in the report and in CP6 Part 3, whatever they are.*

## Part 1 — Protocol (fixed before tuning, D-044)

### Why a second iteration
The pre-registered fuzzy rule base of CP4 (FIS-full) did not beat the paper's coefficient formula (H1 rejected). The analysis of the first iteration measured two concrete weaknesses and one dominant factor:

1. **Trust leak.** FIS-full gives the noisy original pixel about 30 % of the total trust, the paper's formula about 0.1 % (sy2, 15 % noise).
2. **Inputs confounded by noise.** Dev = |y − (ξ+ϑ)/2| and Dis = |ξ − ϑ| cannot separate an edge from noise once ξ itself is noisy.
3. **Reward factor σ.** In the single-factor ablation (C2) a larger σ closes most of the high-noise reproduction gap; σ is the most influential under-determined quantity.

### Candidates
| ID | Name | Change | Targets |
|---|---|---|---|
| A | FIS-bounded α | same rule base; the α output universe is shrunk to the range that the paper's α takes | weakness 1 |
| B | FIS-impulse | third input Imp = \|y − median3×3(y)\| (an impulse/noise detector) with rules such as *IF Imp is Large THEN α is Low* | weakness 2 |
| C | FIS-σ | a small Mamdani system maps an image-level noise estimate to the reward factor σ of the local term; α, β, γ from the paper's formula | factor 3 |
| — | combinations | e.g. C + B | |

**Caveat.** The ideas for B and C were derived from observations on the test seeds (the D-041 diagnosis and the C2 ablation). The test is therefore blind to the parameters of the new variant, not to its idea. This is stated in the report.

### Data split
- **Tuning set:** sy1, sy2, sy3 × mixed noise 1, 5, 10, 15 % × seeds 100–104 (noise realizations used nowhere else).
- **Test set (looked at once):** seeds 0–9 of the same grid (identical noise and initial memberships as E5-main), the 8 BSDS500 images (gray and colour, 5 % mixed noise, seeds 0–9) and the single noise types of C1.

### Budget and selection
- At most **12 configurations** are run on the tuning set; every one, including failures, is logged in `results/tables/e8_tuning_log.csv`.
- **Selection rule:** highest mean ACC on the tuning set (mean over the four noise levels of the per-level mean); ties (< 0.1 point) go to the simpler configuration. The selected variant should not be more than 1 point below ASRFCM-paper at any level; if no configuration satisfies this, the best one is still tested and the result reported as negative.

### Controls in the test
FCM, ASRFCM-paper (σ = 0.3), FIS-full, FIS-split and **ASRFCM with a fixed σ = 0.9**. The last control separates the value of the fuzzy rule from the value of simply using a larger σ.

## Part 2 — Tuning outcome and pre-registration (committed before the test run, D-045)

### Tuning (seeds 100–104 only)
9 of the 12 allowed configurations were run; all are listed, with the four references, in `results/tables/e8_tuning_log.csv` (mean ACC over the four levels):

| Configuration | Mean ACC | Note |
|---|---|---|
| ref: ASRFCM-paper | 97.74 | σ = 0.3 |
| ref: σ = 0.9 (fixed) | 98.85 | |
| ref: FIS-full / FIS-split | 93.05 / 96.64 | first iteration |
| T1 A (α scale 0.002) | 96.70 | ≈ FIS-split |
| T2 B (Imp input) | 93.98 | |
| T3 A+B | 96.70 | |
| T4 / T5 C (image level) | 98.85 / 98.85 | ≈ fixed σ = 0.9 |
| T6 C (pixel level) | 98.84 | |
| **T7 C, output Large = 0.95** | **98.88** | **selected** |
| T8 C+A | 98.56 | ≥ ASRFCM-paper at every level |
| T9 C+split | 98.51 | |

The α scale 0.002 of candidate A is the median ratio between the paper's α share (≈ 0.12 %) and the FIS-full α share (28–45 %) on seed 100.

### Selected variants
- **Primary: FIS-σ (T7).** Input *Noise* = median(|HH|)/0.6745 of the one-level Haar transform of the image (≈ 0.07, 0.16, 0.25, 0.31 at 1, 5, 10, 15 % mixed noise). Terms Low trap(0, 0, 0.05, 0.15), Medium tri(0.05, 0.15, 0.25), High trap(0.15, 0.25, 0.5, 0.5). Output σ: triangles centred at 0.3 (Small), 0.6 (Medium), 0.95 (Large). Rules: Low → Small, Medium → Medium, High → Large. Mamdani, min/max, centroid. α, β, γ from the paper's formula.
- **Secondary: FIS-σ+A (T8)**, declared here although not chosen by the rule: FIS-σ with output 0.3/0.6/0.9 plus the CP4 coefficient rule base with α scale 0.002.

### Hypotheses
- **H5 (primary).** On the synthetic test grid (sy1–sy3, mixed noise, seeds 0–9), FIS-σ has a higher mean ACC than ASRFCM-paper at 10 % and at 15 % noise, each significant (paired two-sided Wilcoxon over the 30 image–seed pairs, p < 0.05), and at 1 % and 5 % its mean ACC is not more than 0.5 point lower on any image.
- **H5-control (expected null).** FIS-σ and a fixed σ = 0.9 differ by less than 0.5 point in mean ACC on every synthetic mixed-noise setting. A benefit of the fuzzy rule over the fixed value can only appear for low noise or other noise types (0 % and the single noise types of C1) or on natural images (BSDS500).
- **H6 (secondary).** FIS-σ+A has a mean ACC ≥ ASRFCM-paper at every level on every image, with no significant loss (p < 0.05).
- **BSDS500** (gray and colour, 5 %): reported per image without a threshold; FIS-σ vs ASRFCM-paper and vs σ = 0.9 (Wilcoxon over 10 seeds).

### Test runs (each run once)
`experiments/contribution/second_iteration.yaml`, `robustness_second.yaml`, `bsds_second.yaml`, `bsds_rgb_second.yaml`; analysis `experiments/analyze_second_iteration.py`.

## Part 3 — Test results (single run after the pre-registration commit)

Verdicts computed by `experiments/analyze_second_iteration.py` (`results/tables/e8_hypotheses.csv`):

| Hypothesis | Criterion | Value | Verdict |
|---|---|---|---|
| H5 | FIS-sigma > paper at 10 % and 15 % (pooled Wilcoxon p<0.05) | 10%: +0.92 (p=1.9e-09); 15%: +3.59 (p=1.9e-09) | holds |
| H5 | FIS-sigma not >0.5 below paper at 1 % and 5 % on any image | worst -0.01 | holds |
| H5 | overall | — | holds |
| H5-control | |FIS-sigma - sigma 0.9| < 0.5 on every setting (expected null) | range -0.02 to +0.19 | holds |
| H6 | FIS-sigma+A mean ACC >= paper on every image and level | worst +0.00 | holds |
| H6 | no significant loss (per image and level, p<0.05) | 0 significant losses | holds |
| H6 | overall | — | holds |

- FIS-σ vs ASRFCM-paper, pooled over sy1–sy3 (n = 30): -0.00 / +0.06 / +0.92 / +3.59 ACC points at 1 / 5 / 10 / 15 % mixed noise; at 15 % sy2/sy3 reach 97.00/95.08 % (paper's settings 92.38/89.13 %).
- FIS-σ+A vs ASRFCM-paper: +0.11 / +0.13 / +0.64 / +2.34.
- BSDS500, 5 %, mean over 8 images: gray 79.85 → FIS-σ 80.98 (fixed σ = 0.9: 80.98; FIS-σ+A 80.51); colour 85.29 → 85.43 (fixed: 85.54; FIS-σ+A 85.39).
- Noise types: mixed 20 % 86.90 → 93.49; salt-and-pepper 20 % 99.35 → 99.35 (fixed σ = 0.9: 99.66) — the median-based noise estimate does not see sparse impulses (D-046).

**Interpretation.** The diagnosis of the first iteration is confirmed: bounding the trust in the noisy pixel removes the loss of the first rule base, and adapting the reward factor closes most of the high-noise reproduction gap. As pre-registered (H5-control), the fuzzy σ is not better than the best fixed value on mixed noise; its contribution is the automatic choice of σ.

### Addendum (15.11.2026) — comparison with the values printed in [1]

Added to the report (Table X column "Reported [1]", paragraph in Section VIII-I, abstract, conclusion, limitations) and as slide 20. It is descriptive only and does not change the verdicts above, which compare against our implementation of the method under identical noise. Against the printed values (other implementation, other noise realizations): at 1–5 % FIS-σ is within −0.06 … +0.14 points (agreement); at 15 % on sy2/sy3 it is still 1.53/2.28 points below, down from 6.15/8.23 with the paper's settings (≈ 73 % of the gap closed); on colour BSDS500 85.43 vs 87.36 %. The second iteration therefore improves the method but does not exceed the results reported in [1] (D-047).
