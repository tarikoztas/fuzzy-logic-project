# Implementation Decisions and Deviations

Public log of the choices made where the reference paper (Wu et al., ESWA 256:124943, 2024) is ambiguous, inconsistent, or silent. Code comments refer to these IDs (`D-xxx`). Each entry states the choice and, where available, the evidence for it.

## Scope

| ID | Decision |
|---|---|
| D-005 / D-017 | **Minimum reproduction requirement (MRR):** baseline FCM (Alg. 1); the full proposed method (local information ξ, Alg. 2; DTCWT-domain non-local information ϑ; adaptive coefficients α, β, γ; sparse-regularized FCM, Alg. 3); reproduction of Tables 2–8 (sy1–sy3 × 1/5/10/15 % mixed noise) and the ablation of Table 1; the 8 BSDS500 images of Table 9. The other 8 comparison methods are not re-implemented; their paper-reported values are quoted and labelled as such. |
| D-004 / D-033 | **Fuzzy-system components.** The paper's method is fuzzy clustering, not a rule-based inference system. Its components are mapped to the course terminology (inputs, membership functions = U, objective minimisation, defuzzification = argmax). In addition, the proposed extension adds an explicit Mamdani fuzzy inference system (fuzzification, IF–THEN rule base, inference, defuzzification), see D-006. |
| D-006 | **Proposed extension.** Primary: a Mamdani fuzzy inference system that computes the per-pixel constraint coefficients α, β, γ from the deviations |y−ξ| and |y−ϑ|, replacing the closed-form Eqs. 13–19. Compared variants: membership-function shape (triangular vs Gaussian), defuzzification (centroid, bisector, mean of maxima) and a zero-order Sugeno version. Supporting analyses: robustness per noise type and density (Gaussian, speckle, salt-and-pepper, mixed; 0–20 %) and a single-factor ablation (reward ratio ρ, rounding, sign of ΔG in Eqs. 15–16). |
| D-015 | 10 seeds (0–9) per setting; mean ± std; the seed fixes both the noise realisation and the initial memberships, which are shared by all methods. |

## Data and noise

| ID | Decision |
|---|---|
| D-030 / D-008 | sy1–sy3 re-created from the raster of the paper's Fig. 9 (`tools/extract_synthetic_from_figure.py`): crop, resize to 256×256, nearest gray level, 5×5 median. Measured gray levels: sy1 {0, 255}, sy2 {0, 107, 255}, sy3 {0, 107, 222} → K = 2, 3, 3. Same shapes and levels as the paper, not the original files. |
| D-027 | "p % mixed noise" = Gaussian (mean 0, variance p) → multiplicative/speckle (J = I + n·I, n uniform, variance p) → salt-and-pepper (density p), applied in turn and clipped to [0, 1]. Evidence: a classifier that knows the true gray levels reaches an ACC within 2 points of the paper-reported FCM ACC in all 12 image/noise cases (`results/tables/noise_oracle_check.csv`). |
| D-029 | BSDS500 from the official archive; color → gray with BT.601 weights (0.2989 R + 0.5870 G + 0.1140 B). Each image has 5–6 human segmentations with 3–51 regions; the ground-truth/K protocol is fixed in experiment E6 and its effect is reported. |

## Metrics

| ID | Decision |
|---|---|
| D-028 | Clusters are matched to classes with the Hungarian algorithm; F-score is the macro average over classes; NMI = 2·MI/(H1+H2) without matching; Kappa is Cohen's kappa after matching; 0·ln 0 = 0 in V_PE. Cross-checked against scikit-learn. |
| D-031 | **The paper's Kappa is not Cohen's kappa for K > 2.** Solving Eq. 35 for the chance agreement p_e with the paper's own ACC/Kappa pairs gives p_e = 0.5556 in all 24 three-class cells (sy2, sy3; FCM and the proposed method; 1–15 % noise), independent of the prediction. The constant fits p_e = (1/K)² + ((K−1)/K)². We report Cohen's kappa (`Kappa`) and, only for comparison with the paper, this rescaled ACC (`Kappa_paper`). |

## Method details

| ID | Decision |
|---|---|
| D-014 | Reward-set size floor(0.618·(N_R−1)) (Fig. 1 shows 4 of 8 neighbours; the text's ceiling would give 5). |
| D-032 | **Local information ξ is implemented as written in Eqs. 5–9 (σ = 0.3, N_R = w²).** The similarity values printed in the paper's Figs. 2–3 reproduce its ξ values (166, 175) but are inconsistent with Eqs. 5–6: their reward/penalty weight ratio is ≈19 (σ ≈ 0.9) and they vary with the neighbour's gray value rather than with its similarity to the centre. Our ξ for the two examples: 167.9 and 197.7. |
| D-012 | Eq. 10 is implemented with y_q (the text has y_j, which makes the weighted sum degenerate). |
| D-010 | Non-local means on the complex DTCWT sub-bands: weights from the magnitude, the same weights applied to the real and imaginary parts; one decomposition level. |
| D-013 | Eqs. 15–16 are implemented as printed, k·exp(y − ξ) (signed); the variant k·exp(|y − ξ|) is evaluated in the ablation. |
| D-011 | If hard thresholding zeroes a whole column of η, its largest element is kept (set to 1 after normalisation). |
| — | Image borders: symmetric (mirror) padding. Sort ties keep raster order. Flat windows (τ = 0): S = 1. |

## Process

| ID | Decision |
|---|---|
| D-019 | Report in English, IEEE two-column conference layout, 8–12 pages excluding references; built from HTML with a headless browser (no LaTeX on the build machine). |
| D-020 | All code written from scratch; no official author implementation was used. |
| D-021 | Presentation delivered as PDF (and PPTX); the live demo runs offline on the student's laptop; the repository is public. |
| D-034 | Working notes (Turkish planning documents) are kept outside the repository; this file, `report/checkpoints/` and the report carry the public record. Generative-AI use is disclosed in the report. |
