"""Experiment E1: baseline FCM on sy1-sy3 with mixed noise, compared with the
FCM column the paper reports (Tables 2-8).

Usage:
    python experiments/baseline/run_baseline.py --config experiments/baseline/config.yaml

Writes one CSV row per run and a summary table (our mean +- std vs the paper).
Every number in the summary comes from these runs; paper numbers come from
results/tables/paper_reported_fcm_vs_ours.csv and are labelled as such.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.data import noise, synthetic  # noqa: E402
from src.eval.metrics import evaluate  # noqa: E402
from src.fcm.baseline_fcm import fcm  # noqa: E402

PAPER_CSV = ROOT / "results" / "tables" / "paper_reported_fcm_vs_ours.csv"
METRICS = ["VPC", "VPE", "ACC", "F", "NMI", "Kappa", "Kappa_paper", "Iterations"]
# Naming in the paper CSV. Our Cohen "Kappa" has no paper counterpart for K > 2
# (D-031), so the paper's Kappa column is compared with "Kappa_paper".
PAPER_METRIC_NAME = {"F": "Fscore", "Kappa": None, "Kappa_paper": "Kappa"}


def run(cfg: dict) -> pd.DataFrame:
    rows = []
    for name in cfg["images"]:
        s = synthetic.load(name)
        for pct in cfg["noise"]["levels_pct"]:
            for seed in cfg["seeds"]:
                noisy = noise.add_noise(s.image, cfg["noise"]["kind"], pct / 100, seed)
                res = fcm(noisy, s.K, seed=seed, **cfg["fcm"])
                m = evaluate(s.labels, U=res.U)
                rows.append({"method": "FCM", "image": name, "noise_kind": cfg["noise"]["kind"],
                             "noise_pct": pct, "seed": seed, **m, "Iterations": res.n_iter,
                             "time_s": res.time_s})
            print(f"{name} {pct:>2}%: done", flush=True)
    return pd.DataFrame(rows)


def summarize(runs: pd.DataFrame) -> pd.DataFrame:
    paper = pd.read_csv(PAPER_CSV)
    paper = paper[paper["method"] == "FCM"]
    out = []
    for (name, pct), g in runs.groupby(["image", "noise_pct"]):
        for met in METRICS:
            pm = paper[(paper["metric"] == PAPER_METRIC_NAME.get(met, met)) & (paper["image"] == name)  # None -> no match
                       & (paper["noise_pct"] == pct)]["value"]
            ours = g[met].mean()
            out.append({"image": name, "noise_pct": pct, "metric": met,
                        "ours_mean": round(ours, 2), "ours_std": round(g[met].std(ddof=0), 2),
                        "paper_reported": float(pm.iloc[0]) if len(pm) else float("nan"),
                        "diff_ours_minus_paper": round(ours - pm.iloc[0], 2) if len(pm) else float("nan")})
    return pd.DataFrame(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=ROOT / "experiments" / "baseline" / "config.yaml")
    cfg = yaml.safe_load(ap.parse_args().config.read_text(encoding="utf-8"))
    runs = run(cfg)
    summary = summarize(runs)
    for key, df in (("runs_csv", runs), ("summary_csv", summary)):
        path = ROOT / cfg["output"][key]
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        print(f"saved {path.relative_to(ROOT)}")
    wide = summary.pivot_table(index=["metric", "image"], columns="noise_pct",
                               values=["ours_mean", "paper_reported"]).round(2)
    print(wide.to_string())


if __name__ == "__main__":
    main()
