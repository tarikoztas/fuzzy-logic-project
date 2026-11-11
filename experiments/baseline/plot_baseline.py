"""Figure for E1: our FCM vs paper-reported FCM (from results/tables/e1_fcm_vs_paper.csv).

Usage:  python experiments/baseline/plot_baseline.py
Output: results/figures/e1_fcm_vs_paper.{png,pdf}
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.viz.plots import ours_vs_paper_grid  # noqa: E402


def main() -> None:
    summary = pd.read_csv(ROOT / "results" / "tables" / "e1_fcm_vs_paper.csv")
    out = ROOT / "results" / "figures" / "e1_fcm_vs_paper"
    out.parent.mkdir(parents=True, exist_ok=True)
    ours_vs_paper_grid(summary, ["ACC", "NMI", "VPC", "Iterations"], ["sy1", "sy2", "sy3"], "FCM", str(out))
    print(f"saved {out.relative_to(ROOT)}.png/.pdf")


if __name__ == "__main__":
    main()
