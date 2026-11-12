"""Figures for the reproduction experiments (E1, E2, E3), made from the result CSVs.

Usage:  python experiments/plot_reproduction.py
Output: results/figures/e1_fcm_vs_paper.*, e2_asrfcm_vs_paper.*, e3_ablation.*
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402

from experiments.common import FIGURES, TABLES  # noqa: E402
from src.viz.plots import ablation_dots, ours_vs_paper_grid  # noqa: E402


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    images = ["sy1", "sy2", "sy3"]
    for csv, label, stem in (("e1_fcm_vs_paper.csv", "FCM", "e1_fcm_vs_paper"),
                             ("e2_asrfcm_vs_paper.csv", "ASRFCM", "e2_asrfcm_vs_paper")):
        if (TABLES / csv).exists():
            ours_vs_paper_grid(pd.read_csv(TABLES / csv), ["ACC", "NMI", "VPC", "Iterations"], images,
                               label, str(FIGURES / stem))
            print(f"saved results/figures/{stem}.png/.pdf")
    if (TABLES / "e3_ablation_vs_paper.csv").exists():
        ablation_dots(pd.read_csv(TABLES / "e3_ablation_vs_paper.csv"), ["ACC", "VPC", "Iterations"],
                      str(FIGURES / "e3_ablation"))
        print("saved results/figures/e3_ablation.png/.pdf")


if __name__ == "__main__":
    main()
