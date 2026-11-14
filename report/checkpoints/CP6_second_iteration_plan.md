# CP6 — Second Iteration of the Contribution (protocol and pre-registration)

*Part 1 was committed before any tuning run; Part 2 (selected variant and hypothesis H5) is committed before the single test run. Results are reported in the report and in CP6 Part 3, whatever they are.*

## Part 1 — Protocol (fixed before tuning, D-044)

### Why a second iteration
The pre-registered fuzzy rule base of CP4 (FIS-full) did not beat the paper's coefficient formula (H1 rejected). The analysis of the first iteration measured two concrete weaknesses and one dominant factor:

1. **Trust leak.** FIS-full gives the noisy original pixel about 30 % of the total trust, the paper's formula about 0.1 % (sy2, 15 % noise).
2. **Inputs confounded by noise.** Dev = |y − (ξ+ϑ)/2| and Dis = |ξ − ϑ| cannot separate an edge from noise once ξ itself is noisy.
3. **Reward factor σ.** In the single-factor ablation (C2) a larger σ closes most of the high-noise reproduction gap; σ is the most influential under-determined quantity.

### Candidates
| ID | Name | Change | Targets |
|---|---|---|---|
| A | FIS-bounded α | same rule base; the α output universe is shrunk to the range that the paper's α takes | weakness 1 |
| B | FIS-impulse | third input Imp = \|y − median3×3(y)\| (an impulse/noise detector) with rules such as *IF Imp is Large THEN α is Low* | weakness 2 |
| C | FIS-σ | a small Mamdani system maps an image-level noise estimate to the reward factor σ of the local term; α, β, γ from the paper's formula | factor 3 |
| — | combinations | e.g. C + B | |

**Caveat.** The ideas for B and C were derived from observations on the test seeds (the D-041 diagnosis and the C2 ablation). The test is therefore blind to the parameters of the new variant, not to its idea. This is stated in the report.

### Data split
- **Tuning set:** sy1, sy2, sy3 × mixed noise 1, 5, 10, 15 % × seeds 100–104 (noise realizations used nowhere else).
- **Test set (looked at once):** seeds 0–9 of the same grid (identical noise and initial memberships as E5-main), the 8 BSDS500 images (gray and colour, 5 % mixed noise, seeds 0–9) and the single noise types of C1.

### Budget and selection
- At most **12 configurations** are run on the tuning set; every one, including failures, is logged in `results/tables/e8_tuning_log.csv`.
- **Selection rule:** highest mean ACC on the tuning set (mean over the four noise levels of the per-level mean); ties (< 0.1 point) go to the simpler configuration. The selected variant should not be more than 1 point below ASRFCM-paper at any level; if no configuration satisfies this, the best one is still tested and the result reported as negative.

### Controls in the test
FCM, ASRFCM-paper (σ = 0.3), FIS-full, FIS-split and **ASRFCM with a fixed σ = 0.9**. The last control separates the value of the fuzzy rule from the value of simply using a larger σ.
