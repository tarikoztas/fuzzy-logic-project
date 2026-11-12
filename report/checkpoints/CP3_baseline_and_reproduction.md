# CP3 — Baseline System and Reproduction Results

All numbers below come from `results/tables/*.csv` produced by the scripts named in each section (10 seeds, mean). Paper numbers are labelled *paper-reported*.

## 1. Implemented system

| Module | Paper | Tests |
|---|---|---|
| `src/fcm/baseline_fcm.py` | FCM, Eqs. 1–3, Alg. 1 | `tests/test_fcm_baseline.py` |
| `src/fcm/local_info.py` | local information ξ, Alg. 2, Eqs. 5–9 | `tests/test_local_info.py` (Fig. 1 reward/penalty sets reproduced exactly) |
| `src/fcm/nonlocal_wavelet.py` | DTCWT + non-local means ϑ, Eqs. 10–11 | `tests/test_nonlocal.py` (vectorised NLM equals a direct transcription of Eqs. 10–11) |
| `src/fcm/adaptive_params.py` | α, β, γ, Eqs. 13–19 | `tests/test_adaptive.py` |
| `src/fcm/sparse_fcm.py`, `src/fcm/pipeline.py` | sparse-regularised FCM, Alg. 3, Eqs. 20–29 | `tests/test_sparse_fcm.py` (reduces exactly to FCM when the extra terms are switched off) |

Run time on a 256×256 image (one core, Windows laptop): ξ ≈ 0.08 s, ϑ ≈ 0.6 s, clustering 0.05–0.3 s.

## 2. E1 — FCM vs paper-reported FCM (Tables 2–8)
`experiments/baseline/run_baseline.py`. Mean |ours − paper| over sy1–sy3 × {1, 5, 10, 15} %: ACC 0.63 (max 1.85), F 0.64, NMI 1.37, V_PC 0.46, V_PE 0.85, Kappa_paper 1.42 points; our FCM needs on average 4.6 fewer iterations. The baseline is reproduced closely, which also supports our reading of the mixed noise (D-027).

## 3. E2 — proposed method vs paper-reported "Ours" (Tables 2–8)
`experiments/proposed/run_proposed.py`.

| ACC (%) | 1 % ours / paper | 5 % | 10 % | 15 % |
|---|---|---|---|---|
| sy1 | 99.99 / 99.89 | 99.91 / 99.86 | 99.72 / 99.75 | 99.34 / 99.56 |
| sy2 | 99.58 / 99.43 | 99.24 / 99.22 | 97.82 / 99.04 | 92.38 / 98.53 |
| sy3 | 99.95 / 99.84 | 99.22 / 99.43 | 96.62 / 98.91 | 89.13 / 97.36 |

Mean |ours − paper|: ACC 1.57, F 1.71, NMI 5.58, V_PC 1.51, V_PE 2.53, Kappa_paper 3.52 points. Up to 5 % noise (and for sy1 at every level) the reproduction is within about 0.5 points; the method improves FCM by up to 37 ACC points (sy3, 10 %). At 10–15 % noise on the three-class images our results are lower than reported (largest gap 8.2 ACC points, sy3 15 %) and need more iterations (34 vs 18).

**Why the gap at high noise.** On its own, ϑ remains highly separable at 15 % noise (FCM on ϑ: 97 % ACC), but ξ computed with Eqs. 5–9 as written (σ = 0.3) is weak (≈ 80 %), and since β ≈ γ the weak local term pulls the result down. The paper's own worked examples (Figs. 2–3) use reward/penalty weights corresponding to σ ≈ 0.9, not 0.3 (D-032), which would make ξ much stronger. We keep σ = 0.3 in the baseline and study σ in E4/E5 instead of tuning it to match.

## 4. E3 — ablation (Table 1)
`experiments/ablation/run_ablation.py`, 5 % noise.
- Same qualitative conclusions as the paper: the non-local term is the most effective single component; all three together give the best (or tied-best) ACC on every image (sy1 99.91, sy2 99.24, sy3 99.22; paper 99.52); the sparse step raises V_PC to ≈ 99 % and lowers the number of iterations in most configurations.
- Differences: the local term alone is much stronger in our runs (ACC 97.5–99.9 vs 82.26 reported).
- **The paper's Table 1 is internally inconsistent (D-040):** its "no component" row is plain FCM, yet its V_PC = 70.58, ACC = 75.10, F = 81.09 and 20 iterations match none of the paper's own FCM entries at 5 % in Tables 2–8 (V_PC 92.55 / 85.83 / 84.11 for sy1 / sy2 / sy3). Its ACC/Kappa pairs imply a three-class image (D-031).

## 5. Findings about the paper collected so far

| ID | Finding |
|---|---|
| D-031 | The reported Kappa equals (ACC − p_e)/(1 − p_e) with a constant p_e = 5/9 for K = 3: a rescaled ACC, not Cohen's kappa. |
| D-032 | The similarity values printed in Figs. 2–3 do not follow Eqs. 5–6 (reward/penalty ratio ≈ 19 ⇒ σ ≈ 0.9). |
| D-038 | With [0, 1] intensities and h² = g·w² = 250, all non-local weights lie in [0.996, 1]: the "non-local means" acts as a 15×15 mean filter on each DTCWT sub-band. |
| D-011r | With δ = 0.4 at most one membership per pixel survives the threshold; the reported V_PC/V_PE are reproduced only if columns where none survives keep their unthresholded memberships. |
| D-040 | Table 1's baseline row is inconsistent with Tables 2–8. |

## 6. Next
CP4: an explicit Mamdani fuzzy inference system for α, β, γ (D-033).
