"""Figures of the fuzzy coefficient system: membership functions, control surfaces,
and a worked inference example for one pixel.

Usage:  python experiments/proposed/plot_fis.py
Output: results/figures/fis_membership.*, fis_surfaces.*, fis_inference_example.*,
        results/tables/fis_rule_base.csv, results/tables/fis_inference_example.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402

from experiments.common import FIGURES, save  # noqa: E402
from src.fcm.fis_coefficients import RULE_TABLE, build_fis  # noqa: E402
from src.viz.fis_plots import control_surfaces, inference_example, membership_functions  # noqa: E402


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    membership_functions(str(FIGURES / "fis_membership"))
    membership_functions(str(FIGURES / "fis_membership_tr"), lang="tr")
    control_surfaces(str(FIGURES / "fis_surfaces"))
    # a salt-like pixel near an edge: deviates from the consensus, estimates partly disagree
    ex = inference_example(str(FIGURES / "fis_inference_example"), dev=0.25, dis=0.12, output="gamma")
    inference_example(str(FIGURES / "fis_inference_example_tr"), dev=0.25, dis=0.12, output="gamma", lang="tr")
    rows = [{"rule": f"R{i + 1}", "Dev": dev, "Dis": dis, "alpha": c[0], "beta": c[1], "gamma": c[2]}
            for i, ((dev, dis), c) in enumerate(RULE_TABLE.items())]
    save(pd.DataFrame(rows), "results/tables/fis_rule_base.csv")
    save(pd.DataFrame([{"Dev": 0.25, "Dis": 0.12, **{f"firing_{k}": v for k, v in ex["firing"].items()},
                        **{f"gamma_{k}": round(v, 4) for k, v in ex["crisp"].items()}}]),
         "results/tables/fis_inference_example.csv")
    print("\n".join(build_fis().rule_table()))
    print("example:", ex)


if __name__ == "__main__":
    main()
