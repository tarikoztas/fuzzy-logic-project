# Speaker notes

## 1. Adaptive Sparse-Regularized Fuzzy Clustering for Noisy Image Segmentation

Introduce yourself and the paper. Say what you will show: re-implementation, reproduction, two iterations of a fuzzy-rule extension, and an honest evaluation.

## 2. Image segmentation: what it is and why it matters

Start from the everyday meaning: colouring an image by regions. Point at the figure: plain FCM is confused by the noise, the reference method recovers the regions. This is the problem the whole talk is about.

## 3. The reference paper at a glance

Name the authors and the journal. Explain the idea in one sentence: do not trust a single noisy pixel, combine it with two cleaner estimates and decide per pixel how much to trust each. Details follow in the method section.

## 4. This project: what we did and why it is useful

Say what the listener gains: a checked implementation, interpretable rules and an automatic parameter choice. Mention that the guideline does not require an improvement, but our second iteration did improve the method under identical conditions.

## 5. Outline of the talk

Keep this short (20 seconds).

## 6. Why noisy images are hard for plain fuzzy clustering

Show the noisy images and how FCM fails. If asked: FCM minimises Σ u^m (y − c)² with Σ_i u = 1; the mixed noise is Gaussian + speckle + salt-and-pepper (sy3, 15 %: ACC ≈ 56 %).

## 7. How earlier work helps FCM against noise

If asked for names: local — BCFCM, FCM_S, FGFCM, FLICM, FRFCM; non-local — FCM_SNLS, FALRCM, FSC_LNML; wavelet/sparse — WFCM, SRFCM, DSFCM_N.

## 8. Fuzzy logic in three ideas

Connect to the lectures. If asked: AND = min, implication = min (clipping), aggregation = max; defuzzification by centroid, bisector or mean of maxima; Sugeno uses constant outputs and a weighted average.

## 9. How the method works

Walk through the figure left to right. Orange box = our first iteration (the weights); the second iteration changes σ inside the first opinion. If asked: distance d = α(y−c)² + β(ξ−c)² + γ(ϑ−c)², ξ = local, ϑ = non-local estimate.

## 10. Opinion 1: a fair vote of the neighbours

If asked: reward weight 1+σ, penalty weight 1−σ, times exp(−Δgray²/τ²)·exp(−distance); reward-set size ⌊0.618·(N_R−1)⌋; Fig. 1 of the paper is reproduced exactly (D-014).

## 11. Opinion 2: cleaning in the wavelet domain

If asked: dual-tree complex wavelet transform (DTCWT), 1 low-pass + 6 sub-bands at ±15°, ±45°, ±75°; non-local means with a 15×15 search window and 5×5 patches, h² = 250.

## 12. Weighing the three opinions

If asked: ΔG1 = k·exp(y − ξ), ΔG2 = k·exp(y − ϑ); α = 1/(ΔG1+ΔG2), β = ΔG1, γ = ΔG2 with k = 15; objective Σ u^m d + δ‖U‖₀, hard threshold √δ = 0.63 then normalise; w=5, S=15, υ=4, g=10, σ=0.3, k=15, δ=0.4, m=2.

## 13. The fuzzy systems of the project at a glance

This slide answers the guideline items: inputs/outputs, membership functions, rule base, inference, defuzzification — for the paper and for both iterations.

## 14. How we tested

If asked: mixed noise p % = Gaussian(var p) → speckle(var p) → salt-and-pepper(p); metrics V_PC, V_PE, ACC, F, NMI, Kappa; Hungarian matching of labels; paired Wilcoxon tests; 97 unit tests.

## 15. What the paper reports

These are paper-reported numbers (Tables 1–9), labelled as such everywhere.

## 16. Could we reproduce the paper?

FCM agreement validates images and noise. The gap at high noise on the three-region images is explained on the next slide (the σ setting).

## 17. Which parts matter?

If asked: non-local term alone 97.5–99.6 %, local alone 97.5–99.9 % (paper: 82.26 %); at 5 % noise σ, w and δ change ACC by < 0.4 points, k = 1 degrades, δ mainly controls the iterations.

## 18. Iteration 1: fuzzy rules for the trust weights

Walk through the figure: which rules fire, how the output set is built, the result. If asked: inputs Dev = |y − (ξ+ϑ)/2| and Dis = |ξ − ϑ|; outputs α, β, γ; a post-hoc variant 'split' keeps the paper's α and only splits β : γ.

## 19. Result: the first rules did not improve accuracy

Negative result reported honestly — the guideline does not require an improvement, but it must be analysed. If asked: hypothesis H1 rejected; '*' = paired Wilcoxon p < 0.05.

## 20. Why it failed

This diagnosis is the bridge to the second iteration. If asked: H3 and H4 hold; the rules are best on clean / 1 % noise, where trusting consistent pixels is right.

## 21. Iteration 2: let a fuzzy rule choose σ

Explain the protocol: tuning on seeds 100–104, testing on 0–9; 9 of 12 allowed configurations tried; hypotheses H5/H6 committed before the test. If asked: noise estimate = median(|HH|)/0.6745 of a Haar transform; σ outputs 0.3 / 0.6 / 0.95; two other candidates (bounded α, impulse input) were also tried. The idea came from the earlier test on σ — the test is blind to the parameters, not to the idea.

## 22. Result: a clear gain at high noise

The rule's value is that it picks σ automatically; a fixed σ = 0.9 is as good on mixed noise (differences -0.02 … +0.19). 'Fuzzy σ + bounded trust' (FIS-σ+A) also bounds the trust in the noisy pixel; it makes the first rule base harmless (worst difference +0.00). If asked: p < 0.001 at 10 and 15 %; at 15 % sy2/sy3 reach 97.00/95.08 %.

## 23. Does it work beyond the test images?

If asked: over four noise types at 0–20 % the fuzzy σ differs from a fixed σ = 0.9 by -0.31 … +0.24 points; salt-and-pepper 20 %: estimate 0, fixed 0.9 slightly better.

## 24. Against the paper's own numbers: closer, not better

Separate the two comparisons. Same code, same noise: the fuzzy σ beats the paper's setting at 10–15 % and never loses meaningfully. Against the numbers printed in the paper (other implementation, other noise, so only indicative): equal at low noise, still 1.53/2.28 points below at 15 % on sy2/sy3, down from 6.15/8.23. Do not claim that we beat the paper.

## 25. Real photographs (BSDS500)

The paper's photographs are in colour, so we also ran a colour version of the method (D-043). If asked: split variant 78.70 %, hypothesis H2 rejected.

## 26. What we learned — and the limits

Be clear about what was and was not done; the guideline values the analysis, not only the accuracy. If asked: the 8 comparison methods of the paper were not re-implemented; iteration 2 was tuned on other noise seeds of the same images.

## 27. Conclusion

Summarise in one sentence, thank the audience and invite questions.