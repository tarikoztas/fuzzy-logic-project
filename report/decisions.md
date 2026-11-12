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
| D-035 (revised) | **Non-local means scale: intensities in [0, 1]** (Algorithm 3, step 1 normalises the image to [0, 1]), Gaussian patch kernel (std υ) normalised to sum 1, h² = g·w² = 250. A first version used 0–255 units, chosen with a nearest-true-level classifier; that criterion was wrong because averaging mixed noise shifts the gray levels, which the classifier counts as errors while clustering adapts its centres. Judged by FCM accuracy on ϑ (sy2/sy3, seed 0): 5 % noise 97.4 / 98.8 ([0, 1]) vs 98.9 / 98.7 (0–255); 15 % noise 97.1 / 97.1 ([0, 1]) vs 75.9 / 78.5 (0–255). The 0–255 variant is kept as an ablation option (`nlm_scale`). Odd image sizes are mirror-padded by one row/column for the DTCWT and cropped back. |
| D-038 | **Finding: with the paper's parameters the non-local means is almost a mean filter.** In [0, 1] units the Gaussian-weighted patch distance is at most about 1, so every weight exp(−dist/250) lies in [0.996, 1]; each DTCWT sub-band is effectively averaged over the 15×15 search window (unit test). The edge-preserving behaviour claimed for this step therefore comes from the wavelet decomposition, not from patch similarity. |
| D-013 | Eqs. 15–16 are implemented as printed, k·exp(y − ξ) (signed); the variant k·exp(|y − ξ|) is evaluated in the ablation. |
| D-011 (revised) | **Empty columns after hard thresholding.** With δ = 0.4, √δ = 0.632 > 0.5, so at most one membership per pixel can pass the threshold and for many pixels none does. Two policies are implemented: `keep` (leave that pixel's η unthresholded) and `argmax` (keep only its largest η, i.e. the pixel becomes crisp). `argmax` makes U fully crisp (V_PC = 100, V_PE = 0 for every image), which contradicts the paper's reported V_PC ≈ 99.x / V_PE ≈ 0.4–5; `keep` reproduces that behaviour (e.g. sy2, 5 %, seed 0: V_PC 99.24, V_PE 1.20 vs paper 99.30, 1.00). Default: `keep`; `argmax` is evaluated in the ablation. ACC is practically identical under both. |
| D-036 | The centre update (Eq. 29) uses the membership matrix of the previous iteration after thresholding and normalisation. |
| D-037 | Ablation switches (Table 1): a disabled local or non-local term is removed together with its coefficient; with one corrected image active, α = 1/ΔG and its coefficient is ΔG; with none, α = 1. Disabling the sparse step means δ = 0 (no threshold, no ℓ0 term). With only the original term and δ = 0 the method reduces exactly to FCM (unit test). |
| — | Image borders: symmetric (mirror) padding. Sort ties keep raster order. Flat windows (τ = 0): S = 1. |

| D-040 | **Finding: the paper's Table 1 baseline row is inconsistent with Tables 2–8.** With all components off the method is plain FCM, yet the row reports V_PC 70.58, V_PE 51.85, ACC 75.10, F 81.09, 20 iterations, matching none of the paper's FCM entries at 5 % (e.g. V_PC 92.55 / 85.83 / 84.11 for sy1 / sy2 / sy3). Its ACC/Kappa pairs imply K = 3. We run the ablation on all three images and compare with the paper qualitatively. |
| D-039 | Remaining reproduction gap at 10–15 % noise on sy2/sy3 is attributed to the weak local term under Eqs. 5–9 with σ = 0.3 (see D-032); σ is not tuned in the baseline, its effect is measured in E4/E5. |

| D-041 | **Post-hoc FIS variant (exploratory).** First runs of the pre-registered FIS (CP4) showed that it gives the noisy original pixel a share of about 30 % of the total trust, against about 0.1 % with the paper's formula (sy2, 15 % noise), so noise leaks into the clustering. One exploratory variant was added and labelled as such: `split` keeps the paper's α and the paper's total trust β + γ and uses the FIS only to divide that trust between ξ and ϑ. No further variants are tuned on the results; both FIS modes are evaluated on the full grid, on other noise types and on BSDS500. |

## Process

| ID | Decision |
|---|---|
| D-019 | Report in English, IEEE two-column conference layout, 8–12 pages excluding references; built from HTML with a headless browser (no LaTeX on the build machine). |
| D-020 | All code written from scratch; no official author implementation was used. |
| D-021 | Presentation delivered as PDF (and PPTX); the live demo runs offline on the student's laptop; the repository is public. |
| D-034 | Working notes (Turkish planning documents) are kept outside the repository; this file, `report/checkpoints/` and the report carry the public record. Generative-AI use is disclosed in the report. |
