# CP4 — Contribution Proposal: a Mamdani Fuzzy Inference System for the Constraint Coefficients

*Written before running the contribution experiments (hypotheses and success criteria are fixed here).*

## 1. What changes

In the reference method every pixel j has three trust coefficients in the objective (Eq. 12/20): α_j (original value y_j), β_j (local information ξ_j) and γ_j (non-local information ϑ_j). The paper computes them with a closed-form rule (Eqs. 15–19):

ΔG1 = k·exp(y − ξ), ΔG2 = k·exp(y − ϑ), α = 1/(ΔG1 + ΔG2), β = ΔG1, γ = ΔG2.

We replace this formula by an explicit **Mamdani fuzzy inference system (FIS)** with linguistic variables, membership functions, an IF–THEN rule base, min/max inference and defuzzification. Everything else (ξ, ϑ, sparse FCM, parameters, seeds, noise) stays identical, so any difference in the results is caused by the coefficient rule alone.

## 2. Why (scientific and technical motivation)

1. **The closed form cannot tell the two corrected images apart.** With k = 15 and gray values in [0, 1], ΔG lies in [5.5, 40.8], so α ≈ 0.01–0.1 and β ≈ γ for most pixels. Both corrected images get practically the same weight everywhere.
2. **But they fail in different places (our reproduction, CP3).**
   - With the paper's parameters the non-local step behaves like a 15×15 mean filter on the wavelet sub-bands (D-038). It is a very strong denoiser in flat regions (FCM on ϑ alone: ≈ 97 % ACC at 15 % noise), but it blurs edges.
   - The local term ξ is edge-aware, because the reward set comes from the neighbours with the most typical gray values. However, it is weaker under heavy noise (≈ 80 % ACC at 15 %).
   - The remaining reproduction gap at high noise comes from mixing the two with equal weight (D-039).
3. **The paper's rule has no explicit, inspectable logic.** For example, the signed exponential treats salt and pepper asymmetrically (D-013). A rule base states the intended behaviour in words, can be checked by a human, and connects the method to the course material: fuzzy sets, membership functions, rule-based inference, defuzzification.
4. **Coverage of the guideline's contribution types:**
   - rule-base design;
   - comparison of membership-function shapes;
   - comparison of defuzzification methods;
   - Mamdani vs Sugeno comparison.

   It also makes the fuzzy-system requirements of the reproduction (inputs/outputs, membership functions, rule base, inference, defuzzification) explicit.

## 3. Design

**Inputs (per pixel, gray values in [0, 1]):**
- *Dev* = |y − (ξ + ϑ)/2| — how far the observed pixel is from the consensus of the two corrected estimates (large ⇒ the pixel is probably noise);
- *Dis* = |ξ − ϑ| — how much the two corrected estimates disagree (large ⇒ probably an edge or fine structure, where the mean-like ϑ is unreliable).

Universe [0, 1]. Terms Small / Medium / Large:
- triangular: Small = (0, 0, 0.15), Medium = (0.05, 0.2, 0.35), Large = trapezoid (0.2, 0.4, 1, 1);
- Gaussian variant with the same centres and comparable widths.

**Outputs:** α (trust in y), β (trust in ξ), γ (trust in ϑ). Universe [0, 1]. Terms Low = (0, 0, 0.5), Medium = (0.25, 0.5, 0.75), High = (0.5, 1, 1).

**Rule base (9 rules, AND = min):**

| Dev \ Dis | Small (flat region) | Medium | Large (edge) |
|---|---|---|---|
| **Small** (pixel consistent) | α High, β Medium, γ Medium | α High, β Medium, γ Low | α High, β Medium, γ Low |
| **Medium** | α Medium, β Medium, γ High | α Medium, β High, γ Medium | α Medium, β High, γ Low |
| **Large** (probably noise) | α Low, β High, γ High | α Low, β High, γ Medium | α Low, β High, γ Low |

Reading:
- a pixel that agrees with both estimates keeps its own value;
- a deviating pixel loses trust in its own value;
- in flat regions the strong smoother ϑ is trusted;
- near edges the edge-aware ξ is trusted and ϑ is not.

**Inference and defuzzification:**
- implication = min (clipping), aggregation = max;
- defuzzification = centroid (default), bisector and mean of maxima as variants;
- zero-order Sugeno variant: the same rules with singleton outputs at the centroids of the Mamdani output terms.

**Coefficient scaling:** the three outputs are normalised per pixel to α + β + γ = 1. The memberships of a pixel depend only on ratios of its distances, so this changes only how strongly each pixel weighs in the centre update (Eq. 29). The unnormalised version is an ablation.

**Implementation:** our own vectorised NumPy code (`src/fuzzy/`), computed once per image like ξ and ϑ.

## 4. Hypotheses

- **H1 (main):** ASRFCM with FIS coefficients reaches a higher ACC than ASRFCM with the paper's coefficients at 10–15 % mixed noise on sy2/sy3, and is not worse by more than 0.5 points at 1–5 % noise.
- **H2:** the improvement also appears on the real BSDS500 images (5 % noise), at least in mean ACC over the 8 images.
- **H3:** the choice of membership-function shape and of defuzzification method changes ACC by less than 1 point (the rule base matters more than these details), while mean of maxima gives coarser coefficients and the least stable results.
- **H4:** Sugeno (zero-order) gives results within 1 point of Mamdani-centroid at lower cost.

## 5. Success criteria and analysis

- **Metrics:** ACC (main), F, NMI, Cohen's Kappa, V_PC, V_PE, iterations, time.
- **Statistics:** 10 seeds per setting (the seed fixes the noise and the initial U, shared by all methods). We report mean ± std and a paired two-sided Wilcoxon signed-rank test on per-seed ACC (α = 0.05), per image and noise level.
- **Decision rules:**
  - H1 is supported if the mean ACC gain is positive and significant at 10 % and 15 % for both sy2 and sy3, and no 1–5 % setting loses more than 0.5 points.
  - H2 is supported if the 8-image mean ACC is higher.
  - A negative result is reported as such and analysed.

## 6. Experiment design

All experiments change one factor at a time:
- **E5-main:** {paper, FIS-Mamdani-tri-centroid} × sy1–3 × {1, 5, 10, 15} % × 10 seeds, plus BSDS500 8 images × 5 %.
- **E5-FIS variants:** MF {triangular, Gaussian} × defuzzification {centroid, bisector, MOM} × {Mamdani, Sugeno}, on sy2/sy3 at 5 % and 15 %.
- **E5-robustness (C1):** noise type {Gaussian, speckle, salt-and-pepper, mixed} × density {0, 1, 5, 10, 15, 20} % × {FCM, ASRFCM-paper, ASRFCM-FIS}.
- **E5-ablation (C2):** reward ratio ρ {0.5, 0.618, 0.7, 0.8}; rounding {floor, ceil}; ΔG sign {signed, abs}; σ {0.3, 0.6, 0.9}; empty-column policy {keep, argmax}; NLM scale {1, 255}; FIS normalisation {on, off}.

The rule base and membership functions are fixed in this document before the experiments and are not tuned on the test results; any later change will be recorded as a new decision with its reason.

*Student approval: pending (the student delegated the decision; recorded as D-006-final / D-033).*
