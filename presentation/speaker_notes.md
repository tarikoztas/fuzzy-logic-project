# Speaker notes

## 1. Reproducing an Adaptive Sparse-Regularized Fuzzy Clustering Method for Noisy Image Segmentation — and Extending It with Mamdani Rule Bases

Introduce yourself and the paper. Say what you will show: re-implementation, reproduction, findings about the paper, two iterations of a fuzzy-rule extension, and an honest evaluation.

## 2. Why noisy image segmentation is hard for FCM

Show the noisy images and how FCM fails. Motivation: real images (medical, remote sensing) contain several noise types at once.

## 3. How earlier work adds spatial information to FCM

Explain the four strands; the paper is the only one combining all five ingredients. Closest relatives: SRFCM (sparsity framework) and FSC_LNML (same lab).

## 4. Fuzzy sets, fuzzy clustering and fuzzy inference

Connect to the lectures. FCM is fuzzy because of the membership matrix; the paper has no explicit rule base — this motivates our extension.

## 5. Architecture of the method (and where our extension plugs in)

Walk through the pipeline left to right. Orange box = first iteration of our contribution; the second iteration acts on σ inside the ξ box.

## 6. Local information ξ: golden-ratio reward and penalty sets

Analogy: a jury that down-weights, but does not delete, the most extreme scores. Text says ceil, the figure shows floor — we use floor (D-014).

## 7. Non-local information ϑ in the wavelet domain

Explain DTCWT with the analogy of splitting a song into bass/mid/treble channels. Then the finding: the patch-similarity part is practically inactive with the published parameters.

## 8. Adaptive coefficients and sparse-regularised FCM

Emphasise the scale of the coefficients — it becomes important for our extension.

## 9. The fuzzy systems of the project at a glance

This slide answers the guideline items: inputs/outputs, membership functions, rule base, inference, defuzzification — for the paper and for both iterations.

## 10. Data, noise and protocol

Stress fairness: identical noise realisations and initialisations; only one factor changes at a time.

## 11. What the paper reports

These are paper-reported numbers (labelled as such everywhere).

## 12. Our reproduction vs. the paper (synthetic images)

FCM agreement validates images and noise. The method matches at low noise; at high noise on 3-class images it is lower — explained on the next slides.

## 13. Ablation and sensitivity

The reward factor is the key under-determined quantity; the paper's own worked example corresponds to σ ≈ 0.9. Remember this — it drives the second iteration.

## 14. Six inconsistencies we found in the paper

Each finding has evidence in report/decisions.md (D-031, D-032, D-038, D-011r, D-040, D-042). This is the critical-evaluation part of the guideline.

## 15. A Mamdani rule base for α, β, γ

Walk through the inference example: which rules fire, how the output set is built, three defuzzification results.

## 16. Result: the first rule base did not improve accuracy (H1 rejected)

Negative result reported honestly — the guideline says improvement is not required, but it must be analysed. The next slide shows the analysis.

## 17. Why it failed — and what the variants show

This diagnosis is the bridge to the second iteration: each candidate targets one of these causes.

## 18. Second iteration: a fuzzy reward factor (pre-registered)

Explain the protocol: tuning set separate from the test set, budget, pre-registration. Be open that the idea came from the C2 ablation on the test seeds — the test is blind to the parameters, not to the idea.

## 19. Result: H5 holds, H6 holds

FIS-σ reaches 97.00/95.08 % at 15 % on sy2/sy3, close to the paper-reported 98.53/97.36 %. Honest part: a fixed σ = 0.9 is as good on mixed noise (differences -0.02 … +0.19); the rule's value is choosing σ automatically. FIS-σ+A is the first rule base made harmless and better at low noise.

## 20. Beyond the test grid: noise types and real images

Show that the gain carries over to the real images and to all noise types, and say clearly where the fixed σ = 0.9 is equally good.

## 21. BSDS500 (5 % mixed noise) and the colour finding

Explain the colour finding (D-042) and the multichannel generalisation (D-043).

## 22. What the contribution adds — and its limits

Be clear about what was and was not done; the guideline values the analysis, not only the accuracy.

## 23. Live demo and conclusion

Run the demo with a different noise type than in the report; backup: results/figures/demo_panel.png.