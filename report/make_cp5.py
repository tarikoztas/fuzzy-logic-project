"""Write report/checkpoints/CP5_experimental_results.md from the same CSV-based values as the report.

Usage:  python report/make_cp5.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from report.report_values import compute  # noqa: E402


def strip_html(s: str) -> str:
    s = s.replace("&nbsp;", " ").replace("<sub>", "_").replace("</sub>", "")
    return re.sub(r"<[^>]+>", "", s)


def main() -> None:
    V, readme = compute()
    text = f"""# CP5 — Experimental Results

All numbers are generated from `results/tables/*.csv` by `report/make_cp5.py` (same computation as the report). 10 seeds per setting; paired two-sided Wilcoxon tests over seeds.

## 1. Reproduction (E1–E4)
- FCM vs paper-reported FCM: mean |Δ| ACC {V['E1_acc_mad']} points (max {V['E1_acc_max']}).
- Proposed method vs paper-reported: {V['E2_acc_mad_low']} ACC points up to 5 % noise, {V['E2_acc_mad_high']} at 10–15 % (largest gap {V['E2_acc_maxgap']}).
- Ablation (Table 1): all components {V['E3_full_acc']} % (sy1/sy2/sy3); non-local alone {V['E3_nl_only']} %; local alone {V['E3_local_only']} %.
- Sensitivity: {strip_html(V['E4_text'])}

## 2. Single-factor ablation of the paper's choices (C2)
{strip_html(V['C2_text'])}

## 3. Proposed extension (E5) — CP4 hypotheses
{readme['results']}

- **H1 rejected**: the pre-registered FIS is worse at 10–15 % (by {V['E5_full_acc_drop15']} points at 15 % on sy2/sy3); the exploratory split variant loses {V['E5_split_acc_drop15']} points at 15 %. Significant gains: {V['E5_sig_gains']}.
- **H3 holds** for shape/bisector/Sugeno (≤ {V['FV_full_maxdiff_nomom']} points for full, ≤ {V['FV_split_maxdiff_nomom']} for split); mean of maxima is the exception (+{V['FV_full_mom_gain15']} points for full at 15 %).
- **H4 holds**: Sugeno within {V['FV_sugeno_maxdiff']} points of Mamdani-centroid.

## 4. Robustness per noise type (C1)
{strip_html(V['C1_text'])}

## 5. Real images (E6)
{strip_html(V['E6_text'])}

## 6. Run time (E7)
{strip_html(V['E7_text'])}

## 7. Why the extension did not help
The pre-registered rule base gives the noisy pixel about 30 % of the total trust (paper formula: about 0.1 %), so noise leaks into the clustering; restricting the FIS to the split between ξ and ϑ removes the leak, but the input Dis = |ξ − ϑ| measures the noise of ξ rather than edges at high noise. The rule base was not tuned further on the test data (D-041).
"""
    out = ROOT / "report" / "checkpoints" / "CP5_experimental_results.md"
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
