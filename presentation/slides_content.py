"""Slide specification (15-20 min talk). Numbers come from report/report_values.py (CSV-based).

Guideline Sec. 4 coverage: problem & motivation (2), literature (3), fuzzy-logic background (4),
method & architecture incl. inputs/outputs, membership functions, rules, inference, defuzzification
(5-9), experiments & data (10), paper's results (11), critical evaluation (14, 20), our implementation
and contribution with comparative results (12-13, 15-19), demo (21).
"""
from __future__ import annotations

import pandas as pd

from report.report_values import compute

T = "results/tables/"


def _e5_rows():
    d = pd.read_csv(T + "e5_main_runs.csv")
    w = pd.read_csv(T + "e5_main_wilcoxon.csv")
    rows = []
    for img in ("sy2", "sy3"):
        for p in (5, 15):
            g = d[(d.image == img) & (d.noise_pct == p)].groupby("method").ACC.mean()
            ws = {m: w[(w.image == img) & (w.noise_pct == p) & (w.method == m)].iloc[0] for m in ("FIS-full", "FIS-split")}
            rows.append([f"{img} {p}%", f"{g['FCM']:.1f}", f"{g['ASRFCM-paper']:.2f}",
                         f"{g['FIS-full']:.2f} ({ws['FIS-full'].mean_diff:+.1f}{'*' if ws['FIS-full']['significant_0.05'] else ''})",
                         f"{g['FIS-split']:.2f} ({ws['FIS-split'].mean_diff:+.1f}{'*' if ws['FIS-split']['significant_0.05'] else ''})"])
    return rows


def _e2_rows():
    e1 = pd.read_csv(T + "e1_fcm_vs_paper.csv").query("metric == 'ACC'").set_index(["image", "noise_pct"])
    e2 = pd.read_csv(T + "e2_asrfcm_vs_paper.csv").query("metric == 'ACC'").set_index(["image", "noise_pct"])
    rows = []
    for img in ("sy1", "sy2", "sy3"):
        for p in (5, 15):
            rows.append([f"{img} {p}%", f"{e1.loc[(img, p), 'ours_mean']:.1f} / {e1.loc[(img, p), 'paper_reported']:.1f}",
                         f"{e2.loc[(img, p), 'ours_mean']:.2f} / {e2.loc[(img, p), 'paper_reported']:.2f}"])
    return rows


def slides() -> list[dict]:
    V, _ = compute()
    return [
        {"kind": "title",
         "title": "Reproducing an Adaptive Sparse-Regularized Fuzzy Clustering Method for Noisy Image Segmentation — and Extending It with a Mamdani Rule Base",
         "subtitle": "Tarık Öztaş (1306230040) · Fuzzy Logic term project · İstanbul University-Cerrahpaşa, Computer Engineering",
         "notes": "Introduce yourself and the paper: Wu et al., Expert Systems with Applications 256 (2024) 124943. Say what you will show: re-implementation, reproduction, findings about the paper, a fuzzy-rule extension, and an honest evaluation."},
        {"section": "Problem", "title": "Why noisy image segmentation is hard for FCM",
         "bullets": ["Segmentation = split an image into homogeneous regions",
                     "**Fuzzy C-means**: every pixel belongs to every cluster with a degree u ∈ [0, 1]",
                     "FCM looks only at the gray value of each pixel → noise flips memberships",
                     ["e.g. our FCM on sy3 with 15 % mixed noise: ACC ≈ 56 %"],
                     "Goal of the paper: robust segmentation under **mixed** Gaussian + salt-and-pepper + multiplicative noise, with few iterations"],
         "image": "results/figures/panel_synthetic.png", "caption": "sy1–sy3, 10 % mixed noise: FCM vs. the method (ours)",
         "notes": "Show the noisy images and how FCM fails. Motivation: real images (medical, remote sensing) contain several noise types at once."},
        {"section": "Literature", "title": "How earlier work adds spatial information to FCM",
         "table": {"columns": ["Family", "Examples", "Idea", "Weakness (per [1])"],
                   "rows": [["Local", "BCFCM, FCM_S, FGFCM, FLICM, FRFCM", "average / filter neighbours", "biased if many neighbours are noisy"],
                            ["Non-local", "FCM_SNLS, FALRCM, FSC_LNML", "similar patches anywhere", "keeps noise, blurs in spatial domain"],
                            ["Transform + sparse", "WFCM, SRFCM, DSFCM_N", "wavelet domain, sparse U", "no non-local / adaptive weights"],
                            ["Recent (2023–25)", "Jiao'23, Chen'23, Das'25", "adaptive weights, auto-K", "—"],
                            ["Wu et al. 2024 [1]", "this paper", "local + non-local (DTCWT) + adaptive + ℓ0", "cost O(n⁵)"]],
                   "caption": "33 references verified on Crossref (references/README.md)"},
         "notes": "Explain the four strands; the paper is the only one combining all five ingredients. Closest relatives: SRFCM (sparsity framework) and FSC_LNML (same lab)."},
        {"section": "Fuzzy-logic background", "title": "Fuzzy sets, fuzzy clustering and fuzzy inference",
         "bullets": ["Fuzzy set: membership function μ(x) ∈ [0, 1] (Zadeh 1965)",
                     "FCM: each cluster is a fuzzy set over the pixels; minimise Σ u^m (y − c)², Σ_i u = 1",
                     ["u_ij = 1 / Σ_r (|y−c_i| / |y−c_r|)^(2/(m−1)),  c_i = Σ u^m y / Σ u^m"],
                     "Mamdani inference: fuzzify → rule firing (AND = min) → clip consequents → aggregate (max) → defuzzify",
                     "Defuzzification: centroid, bisector, mean of maxima; Sugeno: constants + weighted average"],
         "image": "results/figures/fis_membership.png", "caption": "membership functions used in our extension",
         "notes": "Connect to the lectures. FCM is fuzzy because of the membership matrix; the paper has no explicit rule base — this motivates our extension."},
        {"section": "Reference method", "title": "Architecture of the method (and where our extension plugs in)",
         "bullets": ["Input: noisy gray image y ∈ [0, 1], number of clusters K",
                     "ξ: local estimate (reward/penalty sets)", "ϑ: non-local estimate in the DTCWT domain",
                     "α, β, γ: per-pixel trust in y, ξ, ϑ", "Sparse FCM: d = α(y−c)² + β(ξ−c)² + γ(ϑ−c)²",
                     "Output: U (K×N), centres, label = argmax U"],
         "image": "results/figures/architecture.png", "narrow_text": True,
         "notes": "Walk through the pipeline left to right. Orange box = our contribution."},
        {"section": "Reference method", "title": "Local information ξ: golden-ratio reward and penalty sets",
         "bullets": ["Sort the neighbours in the w×w window by gray value",
                     "Middle ⌊0.618·(N_R−1)⌋ → **reward set** (weight 1+σ), ends → **penalty set** (1−σ)",
                     ["Fig. 1 of the paper: 8 neighbours → reward {169, 172, 174, 176}, penalty {103, 137, 194, 212} — reproduced exactly by our code"],
                     "Weight = (1±σ) · exp(−Δgray²/τ²) · exp(−distance); ξ = weighted mean",
                     "Analogy: a jury that down-weights (not deletes) the most extreme scores"],
         "notes": "Penalty pixels are down-weighted, not removed, so real edges keep influence. Text says ceil, the figure shows floor — we use floor (D-014)."},
        {"section": "Reference method", "title": "Non-local information ϑ in the wavelet domain",
         "bullets": ["DTCWT: 1 low-pass + 6 complex direction sub-bands (±15°, ±45°, ±75°), near shift-invariant, perfect reconstruction",
                     "Non-local means on all 7 sub-bands: 15×15 search window, 5×5 patches, h² = g·w² = 250",
                     "Inverse DTCWT → ϑ",
                     "**Finding (D-038)**: in [0, 1] units every NLM weight lies in [0.996, 1] → it acts like a 15×15 mean filter; edge preservation comes from the wavelets"],
         "notes": "Explain DTCWT with the analogy of splitting a song into bass/mid/treble channels. Then the finding: the patch-similarity part is practically inactive with the published parameters."},
        {"section": "Reference method", "title": "Adaptive coefficients and sparse-regularised FCM",
         "bullets": ["ΔG1 = k·exp(y − ξ), ΔG2 = k·exp(y − ϑ);  α = 1/(ΔG1+ΔG2), β = ΔG1, γ = ΔG2",
                     ["k = 15 → α ≈ 0.01–0.1, β ≈ γ ≈ 5–40: the original pixel gets ~0.1 % of the trust"],
                     "Objective J = Σ u^m d + δ‖U‖₀; per iteration: centres → η → hard threshold √δ → normalise",
                     "√0.4 = 0.63 > 0.5 → at most one membership per pixel survives; pixels where none survives keep η (D-011r, reproduces the reported V_PC)",
                     "Parameters: w=5, S=15, υ=4, g=10, σ=0.3, k=15, δ=0.4, m=2"],
         "notes": "Emphasise the scale of the coefficients — it becomes important for our extension."},
        {"section": "Fuzzy system", "title": "Fuzzy-system view required by the course guideline",
         "table": {"columns": ["Element", "Paper (fuzzy clustering)", "Our extension (Mamdani FIS)"],
                   "rows": [["Inputs", "y, ξ, ϑ, K", "Dev = |y − (ξ+ϑ)/2|, Dis = |ξ − ϑ|"],
                            ["Membership functions", "u_ij (Eq. 2/28)", "Small/Medium/Large, triangular or Gaussian"],
                            ["Rule base", "implicit (objective minimisation)", "9 IF–THEN rules"],
                            ["Inference", "alternating optimisation", "AND=min, implication=min, aggregation=max"],
                            ["Defuzzification", "argmax u_ij", "centroid / bisector / MOM; Sugeno variant"],
                            ["Outputs", "U, centres, label map", "α, β, γ per pixel"]]},
         "notes": "This slide answers the guideline items: inputs/outputs, membership functions, rule base, inference, defuzzification."},
        {"section": "Experiments", "title": "Data, noise and protocol",
         "bullets": ["sy1–sy3 (256×256, K = 2/3/3) extracted from the paper's Fig. 9; BSDS500 8 images with the 2–4 class ground truths of Fig. 22 (validated: 93.5–99.7 % agreement with human segmentations)",
                     "Mixed noise p % = Gaussian(var p) → speckle(var p) → salt-and-pepper(p) — our reading, validated by the FCM agreement",
                     "10 seeds per setting; same noise and initial U for all methods; paired Wilcoxon tests",
                     f"Metrics: V_PC, V_PE, ACC, F, NMI, Kappa, iterations, time; Hungarian matching; {V['n_tests']} unit tests"],
         "notes": "Stress fairness: identical noise realisations and initialisations; only one factor changes at a time."},
        {"section": "Paper's results", "title": "What the paper reports",
         "bullets": ["Synthetic images (Tables 2–8, mean): ACC 79.58 % (FCM) → 99.23 % (proposed); Kappa 54.92 → 98.30",
                     "Ablation (Table 1): non-local term most effective; all three components best",
                     f"BSDS500 (Table 9): mean ACC {V['E6_paper_fcm_mean']} → {V['E6_paper_ours_mean']} %",
                     "Fewer iterations thanks to sparsity; best or near-best against 8 methods"],
         "notes": "These are paper-reported numbers (labelled as such everywhere)."},
        {"section": "Reproduction", "title": "Our reproduction vs. the paper (synthetic images)",
         "table": {"columns": ["Setting", "FCM ours / paper", "Method ours / paper"], "rows": _e2_rows(),
                   "caption": "ACC (%), mean of 10 seeds vs paper-reported"},
         "image": "results/figures/e2_asrfcm_vs_paper_compact.png",
         "bullets": [f"FCM: mean |Δ| = {V['E1_acc_mad']} ACC points", f"Method: {V['E2_acc_mad_low']} points up to 5 %, {V['E2_acc_mad_high']} at 10–15 %"],
         "notes": "FCM agreement validates images and noise. The method matches at low noise; at high noise on 3-class images it is lower — explained on the next slides."},
        {"section": "Reproduction", "title": "Ablation and sensitivity",
         "bullets": [f"All three components: ACC {V['E3_full_acc']} % (sy1/sy2/sy3); non-local alone {V['E3_nl_only']} %",
                     f"Local alone is strong in our runs ({V['E3_local_only']} %), paper: 82.26 %",
                     "Sensitivity at 5 %: σ, w, δ change ACC by < 0.4 points; k = 1 degrades; δ mainly controls the iterations",
                     f"**σ = 0.9** closes most of the high-noise gap (sy2/sy3 at 15 %: gap {V['C2_sigma_gap']} points)"],
         "image": "results/figures/e3_ablation.png",
         "notes": "The reward factor is the key under-determined quantity; the paper's own worked example corresponds to σ ≈ 0.9."},
        {"section": "Critical evaluation", "title": "Six inconsistencies we found in the paper",
         "bullets": ["**Kappa is a rescaled ACC**: p_e = 5/9 in every 3-class cell → Kappa = (ACC − 5/9)/(4/9)",
                     "**Figs. 2–3** weights ⇒ σ ≈ 0.9, not 0.3; they do not follow Eq. 6",
                     "**NLM ≈ mean filter** with the published parameters (weights 0.996–1)",
                     "**δ = 0.4**: at most one membership survives; reported V_PC needs the 'keep' policy",
                     "**Table 1** 'no component' row ≠ the paper's own FCM results",
                     "**BSDS500 is colour**: FCM on RGB reproduces the reported FCM within 1 point (7/8 images)"],
         "notes": "Each finding has evidence in report/decisions.md (D-031, D-032, D-038, D-011r, D-040, D-042). This is the critical-evaluation part of the guideline."},
        {"section": "Contribution", "title": "Extension: a Mamdani rule base for α, β, γ",
         "bullets": ["Why: the closed form gives β ≈ γ everywhere, but ξ and ϑ fail in different places (ϑ blurs edges, ξ is edge-aware)",
                     "Inputs Dev (pixel vs. consensus) and Dis (disagreement ≈ edge); 9 rules, e.g.",
                     ["IF Dev is Large AND Dis is Small THEN α Low, β High, γ High (noise in a flat region)",
                      "IF Dev is Large AND Dis is Large THEN α Low, β High, γ Low (noise at an edge)"],
                     "Hypotheses and success criteria committed **before** the experiments (CP4)",
                     "Post-hoc variant 'split' (labelled exploratory): keep the paper's α, FIS only splits β : γ"],
         "image": "results/figures/fis_inference_example.png",
         "notes": "Walk through the inference example: which rules fire, how the output set is built, three defuzzification results."},
        {"section": "Contribution", "title": "Result: the rule base did not improve accuracy (H1 rejected)",
         "table": {"columns": ["Setting", "FCM", "paper coeff.", "+FIS full (Δ)", "+FIS split (Δ)"], "rows": _e5_rows(),
                   "caption": "ACC (%), mean of 10 seeds; Δ vs paper coefficients; * Wilcoxon p < 0.05"},
         "bullets": ["Full FIS gives the noisy pixel ~30 % of the trust (paper ~0.1 %) → noise leaks in",
                     "Split: small significant gains at low noise, losses at 15 %: Dis measures ξ's noise, not edges"],
         "notes": "Negative result reported honestly, as the guideline allows; the next slide shows what we learned."},
        {"section": "Contribution", "title": "Variants and robustness per noise type",
         "bullets": [f"Membership shape, bisector vs centroid, Mamdani vs Sugeno: ≤ {V['FV_full_maxdiff_nomom']} points (H3, H4 hold)",
                     "MOM is coarser and partly hides the over-trust of 'full'",
                     "Salt-and-pepper and speckle are almost removed (penalty set catches impulses); Gaussian is harder; the mixed noise is the hardest",
                     "Full FIS is best on clean / 1 % noise (trusts consistent pixels) but over-trusts noisy pixels at high density",
                     "What matters: trust left to the noisy pixel and σ — not the inference details"],
         "image": "results/figures/e5_robustness_acc.png",
         "notes": "C1 robustness analysis: the paper only used mixed noise."},
        {"section": "Real images", "title": "BSDS500 (5 % mixed noise)",
         "bullets": [f"Gray protocol: mean ACC FCM {V['E6_fcm_mean']} → method {V['E6_asr_mean']} % (paper: {V['E6_paper_fcm_mean']} → {V['E6_paper_ours_mean']} %, colour)",
                     f"FIS variants: full {V['E6_full_mean']} %, split {V['E6_split_mean']} % → H2 rejected",
                     f"Colour re-run: FCM {V['E6c_fcm_mean']} % (paper {V['E6_paper_fcm_mean']} %), method {V['E6c_asr_mean']} % "
                     f"(paper {V['E6_paper_ours_mean']} %); FIS split {V['E6c_split_mean']} %"],
         "image": "results/figures/panel_bsds.png",
         "notes": "Explain the colour finding and the colour re-run."},
        {"section": "Discussion", "title": "Limitations and what we would do next",
         "bullets": ["Test images re-created from figures; noise model is an interpretation",
                     "8 comparison methods not re-implemented", "K must be known",
                     "Python implementation: times not comparable with the paper's MATLAB",
                     "Next: noise-robust FIS inputs (e.g. local variance), α constrained to the paper's range, learned membership functions, automatic K"],
         "notes": "Be clear about what was and was not done."},
        {"section": "Demo", "title": "Live demo and conclusion",
         "bullets": ["python demo/demo.py --image sy3 --noise salt_pepper --level 20 --pixel 120 80",
                     "Shows FCM, the method and the FIS variants side by side + the rules firing for one pixel (≈ 15 s, offline)",
                     "Conclusion: the method reproduces well at low/medium noise; σ explains the high-noise gap; six documented inconsistencies; the rule base is interpretable but not better",
                     "Code, data steps, results, decisions: github.com/tarikoztas/fuzzy-logic-project"],
         "notes": "Run the demo with a different noise type than in the report; backup: results/figures/demo_panel.png."},
    ]
