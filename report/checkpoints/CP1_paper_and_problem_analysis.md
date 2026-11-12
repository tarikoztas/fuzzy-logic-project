# CP1 — Paper and Problem Analysis

**Student:** Tarık Öztaş (1306230040) · **Course:** Fuzzy Logic — Term Project
**Reference paper:** J. Wu, X. Wang, Y. Liu, C. Fang, "Adaptive sparse regularized fuzzy clustering noise image segmentation algorithm based on complementary spatial information," *Expert Syst. Appl.*, vol. 256, 124943, 2024, doi: 10.1016/j.eswa.2024.124943.

> All numbers in this note are **paper-reported** values from [1]; no experiment of ours has been run yet.

## 1. Problem

Image segmentation splits an image into regions of similar intensity. Fuzzy C-Means (FCM) lets every pixel belong to every cluster with a degree in [0, 1], but it looks at each pixel **in isolation**. A single noisy pixel (salt-and-pepper, Gaussian, multiplicative/speckle) is therefore easily put in the wrong cluster. Many FCM variants add spatial information, but according to [1] they (i) treat all neighbors as equally important (averaging), (ii) compute non-local similarity in the spatial domain, which can blur edges, and (iii) rarely combine local and non-local information.

## 2. Aim

Robust gray-level segmentation under **mixed noise** (equal parts Gaussian, salt-and-pepper and multiplicative noise) with fewer iterations than FCM, without manually tuning the weight of each information source.

## 3. Fuzzy logic method used

The method stays inside the FCM framework (objective-function-based fuzzy clustering, not a rule-based Mamdani/Sugeno system):

| Component | What it does | Paper |
|---|---|---|
| Local information ξ | Neighbors sorted by gray value; the middle ~61.8 % (golden ratio) form a *reward set* (weight 1+σ), the extremes a *penalty set* (weight 1−σ); combined with gray and spatial similarity → corrected pixel value | Alg. 2, Eq. 5–9 |
| Non-local information ϑ | DTCWT → 1 approximation + 6 directional detail sub-images; non-local means on each; inverse DTCWT | Eq. 10–11 |
| Adaptive weights α, β, γ | Per pixel, from the difference between the noisy pixel and ξ, ϑ: noisy pixels trust ξ, ϑ more (β, γ ↑) and the raw value less (α ↓) | Eq. 13–19 |
| Objective | FCM objective whose distance is a weighted sum of distances of y, ξ, ϑ to the cluster center | Eq. 12 |
| ℓ0 sparse regularization | Penalizes the number of non-zero memberships; solved in three steps: Lagrange (rough memberships η) → hard threshold at √δ → normalization | Eq. 20–29, Alg. 3 |

Mapping to the course's fuzzy-system terms (pending instructor confirmation): **membership functions** = memberships u_ij (Eq. 28) and Gaussian similarity kernels; **inference** = objective minimization; **defuzzification** = argmax over clusters.

## 4. Inputs and outputs

- **Input:** noisy gray-level image normalized to [0, 1]; number of clusters K; parameters w = 5, S = 15, υ = 4, g = 10, σ = 0.3, k = 15, δ = 0.4, m = 2, ε = 10⁻⁶, T = 100 (note: [1] §4.1 states w = 7, §4.4 selects w = 5).
- **Output:** sparse membership matrix U (K × N), cluster centers c, label map (argmax of U).

## 5. Experimental structure in [1]

- **Data:** 3 synthetic images (sy1–sy3) with 1/5/10/15 % mixed noise; 8 BSDS500 images with 5 % noise; qualitative/averaged generalization on AID, MSRC, NASA Earth Observation, COCO.
- **Compared methods (9):** FCM, FGFCM, ADFLICM, FRFCM, DSFCM_N, FCM_SICM, SRFCM, CGFFCM, FSC_LNML.
- **Metrics:** V_PC, V_PE (membership compactness), ACC, F-score, NMI, Kappa (agreement with ground truth), number of iterations, run time.
- **Studies:** parameter sensitivity (σ, w, k, δ), ablation of the three components (Table 1), noise-level stability (0–20 %).
- **Headline result (paper-reported, mean over sy1–sy3 × 4 noise levels):** ACC 79.58 % (FCM) → 99.23 % ([1]); Kappa 54.92 % → 98.30 %; iterations e.g. sy2 at 5 % noise 49 → 12.

## 6. What we will reproduce (MRR proposal)

FCM baseline and the full method of [1]; the synthetic experiment (sy1–sy3 × 1/5/10/15 %) and the ablation (Table 1); BSDS500 images if time allows. Synthetic images are not published, so they will be re-created and results compared in trend, not digit-by-digit.

## 7. Known ambiguities found while reading [1]

Eq. (10) sums y_j instead of y_q; Eq. (15–16) use a signed difference while the text says "absolute"; the hard threshold can zero a whole membership column (0/0 at normalization) because the stated condition √δ ≤ min_j max_i η_ij is not guaranteed; the reward-set size ⌈0.618(N_R−1)⌉ conflicts with Fig. 1 (only floor gives the 4 pixels shown); w = 7 vs. w = 5; the mixed-noise intensity and the label-matching protocol for ACC/F/NMI/Kappa are not specified. Each is resolved as a documented deviation (`report/decisions.md`).
