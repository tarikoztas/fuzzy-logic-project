# CP2 — Implementation Plan and Infrastructure

Reference paper: J. Wu, X. Wang, Y. Liu, C. Fang, ESWA 256 (2024) 124943, doi:10.1016/j.eswa.2024.124943.

## 1. Minimum Reproducible Result (MRR)

1. **Baseline FCM** (Algorithm 1, Eqs. 1–3).
2. **Full proposed method (ASRFCM-CSI):** local spatial information ξ with golden-ratio reward/penalty sets (Algorithm 2, Eqs. 5–9); non-local information ϑ in the DTCWT domain (Eqs. 10–11); per-pixel adaptive coefficients α, β, γ (Eqs. 13–19); sparse-regularized FCM (Algorithm 3, Eqs. 20–29).
3. **Reproduction experiment:** sy1–sy3 × mixed noise {1, 5, 10, 15 %} × 10 seeds; metrics V_PC, V_PE, ACC, F, NMI, Kappa and the number of iterations; compared with the paper-reported FCM and "Ours" columns of Tables 2–8.
4. **Ablation** of Table 1 (local / non-local / sparse on–off, 5 % noise).
5. **Real images:** the 8 BSDS500 images of the paper with 5 % noise (Table 9).

The 8 other methods in the paper's tables are **not re-implemented**; their paper-reported values are quoted for context only. (MRR confirmation from the instructor is pending.)

## 2. Infrastructure built in this checkpoint

| Module | Content | Test |
|---|---|---|
| `src/data/synthetic.py` | sy1–sy3, 256×256, label maps re-created from the paper's Fig. 9; gray levels sy1 {0,255}, sy2 {0,107,255}, sy3 {0,107,222} → K = 2, 3, 3 | `tests/test_data.py` |
| `src/data/noise.py` | Gaussian, speckle (multiplicative), salt-and-pepper, mixed; seeded | `tests/test_noise.py` |
| `src/data/bsds500.py` | 8 BSDS500 images, BT.601 gray, all human ground truths | `tests/test_data.py` (skipped if data absent) |
| `src/eval/matching.py` | Hungarian cluster-to-class matching | `tests/test_metrics.py` |
| `src/eval/metrics.py` | Eqs. 30–35, cross-checked with scikit-learn | `tests/test_metrics.py` |

All 27 tests pass (`python -m pytest`).

## 3. Interpretation of under-specified parts of the paper

| Point | Paper | Our choice | Evidence / note |
|---|---|---|---|
| Synthetic images | shown only in Fig. 9 | extracted from the figure raster | same shapes and gray levels; not the original files |
| "p % mixed noise" | "equal proportions of Gaussian, salt-and-pepper, and multiplicative noise" | Gaussian (var p) → speckle (var p) → salt-and-pepper (density p) | an oracle that knows the true gray levels reaches ACC within 2 points of the paper-reported FCM ACC in all 12 image/noise cases (`results/tables/noise_oracle_check.csv`) |
| Label matching for ACC/F/Kappa | not described | Hungarian matching | standard; NMI needs no matching |
| F-score for K > 2 | Eq. 33 (binary form) | macro average over classes | — |
| BSDS500 gray conversion, ground truth, K | not described | BT.601; annotation with fewest regions; K fixed in experiment E6 | annotations contain 3–51 regions, so this choice affects ACC strongly |

### Noise plausibility check (oracle nearest-level classifier, 10 seeds, mean ACC %)

| Image | 1 % | 5 % | 10 % | 15 % |
|---|---|---|---|---|
| sy1 — oracle (ours) | 99.50 | 94.98 | 85.39 | 77.56 |
| sy1 — FCM (paper-reported) | 99.49 | 95.20 | 86.18 | 77.97 |
| sy2 — oracle (ours) | 97.41 | 77.37 | 66.90 | 61.61 |
| sy2 — FCM (paper-reported) | 97.82 | 77.16 | 67.75 | 62.68 |
| sy3 — oracle (ours) | 96.29 | 73.03 | 61.33 | 55.54 |
| sy3 — FCM (paper-reported) | 95.87 | 74.75 | 62.61 | 57.45 |

This is a plausibility check of the noise definition, not a reproduction result: the oracle is not FCM.

## 4. Next (CP3)

FCM baseline (Eqs. 1–3), then ξ, ϑ, α/β/γ and the sparse FCM, each with unit tests based on the paper's worked examples (Figs. 1–3), followed by the reproduction experiment.
