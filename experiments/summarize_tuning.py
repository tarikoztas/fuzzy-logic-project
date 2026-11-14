"""Second iteration (D-044): tuning log from the TUNING SET runs (seeds 100-104 only).

Writes results/tables/e8_tuning_log.csv: one row per configuration (references marked),
mean ACC / NMI per noise level, the mean over the four levels, the worst gap to
ASRFCM-paper, the mean reward factor used and the date of the run. Applies the selection
rule of D-044 and prints the selected configuration.

Usage:  python experiments/summarize_tuning.py
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402

from experiments.common import TABLES, save  # noqa: E402

RUNS = TABLES / "e8_tuning_runs.csv"
PAPER = "ref: ASRFCM-paper"


def main() -> None:
    d = pd.read_csv(RUNS)
    assert set(d.seed) <= set(range(100, 105)), "tuning log must only contain tuning seeds"
    acc = d.groupby(["method", "noise_pct"]).ACC.mean().unstack()
    nmi = d.groupby(["method", "noise_pct"]).NMI.mean().unstack()
    rows = []
    for m in acc.index:
        r = {"configuration": m, "reference": m.startswith("ref:")}
        for p in acc.columns:
            r[f"ACC_{p}"] = round(acc.loc[m, p], 2)
        for p in nmi.columns:
            r[f"NMI_{p}"] = round(nmi.loc[m, p], 2)
        r["ACC_mean"] = round(acc.loc[m].mean(), 3)
        r["worst_gap_to_paper"] = round((acc.loc[m] - acc.loc[PAPER]).min(), 2)
        if "sigma_used" in d:
            s = d[d.method == m].sigma_used
            r["sigma_used_mean"] = round(s.mean(), 3) if s.notna().any() else float("nan")
        r["date"] = dt.date.today().isoformat()
        rows.append(r)
    log = pd.DataFrame(rows).sort_values(["reference", "configuration"], ascending=[False, True])
    save(log, "results/tables/e8_tuning_log.csv")
    cand = log[~log.reference].copy()
    print(f"{len(cand)} candidate configurations (budget 12)")
    print(log.drop(columns=["date"]).to_string(index=False))
    ok = cand[cand.worst_gap_to_paper >= -1.0]
    pool = ok if len(ok) else cand
    best = pool.ACC_mean.max()
    tied = pool[pool.ACC_mean >= best - 0.1]
    print("\nwithin 0.1 point of the best (choose the simplest):")
    print(tied[["configuration", "ACC_mean", "worst_gap_to_paper"]].to_string(index=False))


if __name__ == "__main__":
    main()
