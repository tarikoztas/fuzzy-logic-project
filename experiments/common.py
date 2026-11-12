"""Helpers shared by the experiment scripts: running a grid, summarising runs,
and placing our numbers next to the paper-reported ones.

Every summary value is computed from the per-run CSV written by the same script;
paper numbers are read from results/tables/paper_reported_*.csv.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TABLES = ROOT / "results" / "tables"
FIGURES = ROOT / "results" / "figures"
PAPER_MAIN = TABLES / "paper_reported_fcm_vs_ours.csv"
METRICS = ["VPC", "VPE", "ACC", "F", "NMI", "Kappa", "Kappa_paper", "Iterations"]
# Our Cohen "Kappa" has no paper counterpart for K > 2 (D-031): the paper's Kappa is compared with Kappa_paper.
PAPER_NAME = {"F": "Fscore", "Kappa": None, "Kappa_paper": "Kappa"}


def load_config(path: Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def save(df: pd.DataFrame, rel: str) -> Path:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"saved {path.relative_to(ROOT)}")
    return path


def summarize_vs_paper(runs: pd.DataFrame, paper_method: str, by=("image", "noise_pct")) -> pd.DataFrame:
    """Mean/std of our runs per (image, noise) next to the paper-reported value of `paper_method`."""
    paper = pd.read_csv(PAPER_MAIN)
    paper = paper[paper["method"] == paper_method]
    out = []
    for (name, pct), g in runs.groupby(list(by)):
        for met in METRICS:
            pname = PAPER_NAME.get(met, met)
            pm = paper[(paper["metric"] == pname) & (paper["image"] == name) & (paper["noise_pct"] == pct)]["value"]
            ours = float(g[met].mean())
            pv = float(pm.iloc[0]) if len(pm) else float("nan")
            out.append({"image": name, "noise_pct": pct, "metric": met, "ours_mean": round(ours, 2),
                        "ours_std": round(float(g[met].std(ddof=0)), 2), "paper_reported": pv,
                        "diff_ours_minus_paper": round(ours - pv, 2) if len(pm) else float("nan")})
    return pd.DataFrame(out)


def mean_abs_diff(summary: pd.DataFrame) -> pd.DataFrame:
    s = summary.dropna(subset=["paper_reported"]).copy()
    s["absdiff"] = s["diff_ours_minus_paper"].abs()
    return s.groupby("metric")["absdiff"].agg(["mean", "max"]).round(2)


def seeds_from(cfg: dict) -> list[int]:
    return list(cfg["seeds"])


__all__ = ["ROOT", "TABLES", "FIGURES", "METRICS", "load_config", "save", "summarize_vs_paper",
           "mean_abs_diff", "seeds_from", "np", "pd"]
