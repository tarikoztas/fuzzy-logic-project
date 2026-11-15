# Speaker notes

## 1. Reproducing an Adaptive Sparse-Regularized Fuzzy Clustering Method for Noisy Image Segmentation — and Extending It with Mamdani Rule Bases

Introduce yourself and the paper. Say what you will show: re-implementation, reproduction, two iterations of a fuzzy-rule extension, and an honest evaluation.

## 2. Image segmentation: what it is and why it matters

Start from the everyday meaning: colouring an image by regions. Point at the figure: plain FCM is confused by the noise, the reference method recovers the regions. This is the problem the whole talk is about.

## 3. The reference paper at a glance

Name the authors and the journal. Explain the idea in one sentence: do not trust a single noisy pixel, combine it with two cleaner estimates and decide per pixel how much to trust each. Details follow in the method section.

## 4. This project: what we did and why it is useful

Say what the listener gains: a checked implementation, interpretable rules and an automatic parameter choice. Mention that the guideline does not require an improvement, but our second iteration did improve the method under identical conditions.

## 5. Outline of the talk

Keep this short (20 seconds).

## 6. Why noisy image segmentation is hard for FCM

Show the noisy images and how FCM fails. Motivation: real images (medical, remote sensing) contain several noise types at once.

## 7. How earlier work adds spatial information to FCM

Explain the four strands; the paper is the only one combining all five ingredients. Closest relatives: SRFCM (sparsity framework) and FSC_LNML (same lab).

## 8. Fuzzy sets, fuzzy clustering and fuzzy inference

Connect to the lectures. FCM is fuzzy because of the membership matrix; the paper has no explicit rule base — this motivates our extension.

## 9. Architecture of the method (and where our extension plugs in)

Walk through the pipeline left to right. Orange box = first iteration of our contribution; the second iteration acts on σ inside the ξ box.

## 10. Local information ξ: golden-ratio reward and penalty sets

Analogy: a jury that down-weights, but does not delete, the most extreme scores. We round the set size down, as in Fig. 1 of the paper (D-014).

## 11. Non-local information ϑ in the wavelet domain

Explain DTCWT with the analogy of splitting a song into bass/mid/treble channels.

## 12. Adaptive coefficients and sparse-regularised FCM

Emphasise the scale of the coefficients — it becomes important for our extension.

## 13. The fuzzy systems of the project at a glance

This slide answers the guideline items: inputs/outputs, membership functions, rule base, inference, defuzzification — for the paper and for both iterations.

## 14. Data, noise and protocol

Stress fairness: identical noise realisations and initialisations; only one factor changes at a time.

## 15. What the paper reports

These are paper-reported numbers (labelled as such everywhere).

## 16. Our reproduction vs. the paper (synthetic images)

FCM agreement validates images and noise. The method matches at low noise; at high noise on 3-class images it is lower — explained on the next slides.

## 17. Ablation and sensitivity

The reward factor σ is the most influential parameter at high noise. Remember this — it drives the second iteration.

## 18. A Mamdani rule base for α, β, γ

Walk through the inference example: which rules fire, how the output set is built, three defuzzification results.

## 19. Result: the first rule base did not improve accuracy (H1 rejected)

Negative result reported honestly — the guideline says improvement is not required, but it must be analysed. The next slide shows the analysis.

## 20. Why it failed — and what the variants show

This diagnosis is the bridge to the second iteration: each candidate targets one of these causes.

## 21. Second iteration: a fuzzy reward factor (pre-registered)

Explain the protocol: tuning set separate from the test set, budget, pre-registration. Be open that the idea came from the C2 ablation on the test seeds — the test is blind to the parameters, not to the idea.

## 22. Result: H5 holds, H6 holds

FIS-σ reaches 97.00/95.08 % at 15 % on sy2/sy3 (paper-reported 98.53/97.36 %: closer, still below; next slides). Honest part: a fixed σ = 0.9 is as good on mixed noise (differences -0.02 … +0.19); the rule's value is choosing σ automatically. FIS-σ+A is the first rule base made harmless and better at low noise.

## 23. Beyond the test grid: noise types and real images

Show that the gain carries over to the real images and to all noise types, and say clearly where the fixed σ = 0.9 is equally good.

## 24. Against the paper's own numbers: closer, not better

Separate the two comparisons. Controlled (same code, same noise): FIS-σ beats the paper's settings at 10–15 % and never loses meaningfully. Against the numbers printed in the paper (other implementation, other noise realizations, so indicative only): equal at low noise, still 1.53/2.28 points below at 15 % on sy2/sy3, down from 6.15/8.23. Do not claim that we beat the paper.

## 25. Real images: BSDS500 in gray and colour (5 % mixed noise)

Explain why we also ran the colour images: the paper's BSDS500 images are colour photographs; we use a multichannel version of the method (D-043).

## 26. What the contribution adds — and its limits

Be clear about what was and was not done; the guideline values the analysis, not only the accuracy.

## 27. Conclusion

Summarise in one sentence: a small rule system that sets σ from the image recovers most of the accuracy lost at high noise. Thank the audience and invite questions.