# Speaker notes

## 1. Reproducing an Adaptive Sparse-Regularized Fuzzy Clustering Method for Noisy Image Segmentation — and Extending It with a Mamdani Rule Base

Introduce yourself and the paper: Wu et al., Expert Systems with Applications 256 (2024) 124943. Say what you will show: re-implementation, reproduction, findings about the paper, a fuzzy-rule extension, and an honest evaluation.

## 2. Why noisy image segmentation is hard for FCM

Show the noisy images and how FCM fails. Motivation: real images (medical, remote sensing) contain several noise types at once.

## 3. How earlier work adds spatial information to FCM

Explain the four strands; the paper is the only one combining all five ingredients. Closest relatives: SRFCM (sparsity framework) and FSC_LNML (same lab).

## 4. Fuzzy sets, fuzzy clustering and fuzzy inference

Connect to the lectures. FCM is fuzzy because of the membership matrix; the paper has no explicit rule base — this motivates our extension.

## 5. Architecture of the method (and where our extension plugs in)

Walk through the pipeline left to right. Orange box = our contribution.

## 6. Local information ξ: golden-ratio reward and penalty sets

Penalty pixels are down-weighted, not removed, so real edges keep influence. Text says ceil, the figure shows floor — we use floor (D-014).

## 7. Non-local information ϑ in the wavelet domain

Explain DTCWT with the analogy of splitting a song into bass/mid/treble channels. Then the finding: the patch-similarity part is practically inactive with the published parameters.

## 8. Adaptive coefficients and sparse-regularised FCM

Emphasise the scale of the coefficients — it becomes important for our extension.

## 9. Fuzzy-system view required by the course guideline

This slide answers the guideline items: inputs/outputs, membership functions, rule base, inference, defuzzification.

## 10. Data, noise and protocol

Stress fairness: identical noise realisations and initialisations; only one factor changes at a time.

## 11. What the paper reports

These are paper-reported numbers (labelled as such everywhere).

## 12. Our reproduction vs. the paper (synthetic images)

FCM agreement validates images and noise. The method matches at low noise; at high noise on 3-class images it is lower — explained on the next slides.

## 13. Ablation and sensitivity

The reward factor is the key under-determined quantity; the paper's own worked example corresponds to σ ≈ 0.9.

## 14. Six inconsistencies we found in the paper

Each finding has evidence in report/decisions.md (D-031, D-032, D-038, D-011r, D-040, D-042). This is the critical-evaluation part of the guideline.

## 15. Extension: a Mamdani rule base for α, β, γ

Walk through the inference example: which rules fire, how the output set is built, three defuzzification results.

## 16. Result: the rule base did not improve accuracy (H1 rejected)

Negative result reported honestly, as the guideline allows; the next slide shows what we learned.

## 17. Variants and robustness per noise type

C1 robustness analysis: the paper only used mixed noise.

## 18. BSDS500 (5 % mixed noise)

Explain the colour finding and the colour re-run.

## 19. Limitations and what we would do next

Be clear about what was and was not done.

## 20. Live demo and conclusion

Run the demo with a different noise type than in the report; backup: results/figures/demo_panel.png.