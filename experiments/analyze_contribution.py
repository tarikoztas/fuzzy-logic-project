"""Analysis of experiments E4-E7: summary tables, paired Wilcoxon tests and figures.
Every number is computed from the run CSVs written by experiments/run_grid.py
(and experiments/timing/run_timing.py); paper values come from
results/tables/paper_reported_*.csv.

Usage:  python experiments/analyze_contribution.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import wilcoxon  # noqa: E402

from experiments.common import FIGURES, TABLES, save  # noqa: E402
from src.viz.plots import method_lines  # noqa: E402

METRICS = ["ACC", "F", "NMI", "Kappa", "Kappa_paper", "VPC", "VPE", "Iterations"]
MAIN_METHODS = ["FCM", "ASRFCM-paper", "FIS-full", "FIS-split"]


def summarize(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    agg = {}
    for m in METRICS:
        agg[f"{m}_mean"] = (m, "mean")
        agg[f"{m}_std"] = (m, lambda s: s.std(ddof=0))
    return df.groupby(by + ["method"]).agg(**agg).reset_index().round(3)


def paired_tests(df: pd.DataFrame, by: list[str], baseline: str, others: list[str], metric: str = "ACC") -> pd.DataFrame:
    """Paired two-sided Wilcoxon signed-rank test per setting (pairs = seeds)."""
    rows = []
    for key, g in df.groupby(by):
        key = key if isinstance(key, tuple) else (key,)
        base = g[g.method == baseline].set_index("seed")[metric]
        for o in others:
            oth = g[g.method == o].set_index("seed")[metric]
            common = base.index.intersection(oth.index)
            d = (oth[common] - base[common]).values
            if len(d) == 0:
                continue
            p = 1.0 if np.allclose(d, 0) else float(wilcoxon(d, zero_method="zsplit").pvalue)
            rows.append({**dict(zip(by, key)), "method": o, "baseline": baseline, "metric": metric,
                         "mean_diff": round(float(d.mean()), 3), "n": len(d), "p_value": round(p, 4),
                         "significant_0.05": p < 0.05})
    return pd.DataFrame(rows)


def guideline_table(df: pd.DataFrame, baseline: str, improved: list[str], timing: pd.DataFrame | None) -> pd.DataFrame:
    """Guideline Sec. 6.2 format: Metric | Baseline | Improved | Change (mean +- std over all runs)."""
    rows = []
    for m in METRICS:
        b = df[df.method == baseline][m]
        row = {"Metric": m, f"Baseline ({baseline})": f"{b.mean():.2f} ± {b.std(ddof=0):.2f}"}
        for imp in improved:
            v = df[df.method == imp][m]
            row[f"Improved ({imp})"] = f"{v.mean():.2f} ± {v.std(ddof=0):.2f}"
            row[f"Change ({imp})"] = f"{v.mean() - b.mean():+.2f}"
        rows.append(row)
    if timing is not None and not timing.empty:
        t = timing.groupby("method")["total_s"].mean()
        row = {"Metric": "Time per 256x256 image (s, E7)", f"Baseline ({baseline})": f"{t.get(baseline, np.nan):.2f}"}
        for imp in improved:
            row[f"Improved ({imp})"] = f"{t.get(imp, np.nan):.2f}"
            row[f"Change ({imp})"] = f"{t.get(imp, np.nan) - t.get(baseline, np.nan):+.2f}"
        rows.append(row)
    return pd.DataFrame(rows)


def load(name: str) -> pd.DataFrame | None:
    p = TABLES / name
    return pd.read_csv(p) if p.exists() else None


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    timing = load("e7_timing.csv")

    # ---- E5-main (H1) ----
    df = load("e5_main_runs.csv")
    if df is not None:
        s = summarize(df, ["image", "noise_pct"])
        save(s, "results/tables/e5_main_summary.csv")
        save(paired_tests(df, ["image", "noise_pct"], "ASRFCM-paper", ["FIS-full", "FIS-split"]),
             "results/tables/e5_main_wilcoxon.csv")
        save(paired_tests(df, ["image", "noise_pct"], "FCM", ["ASRFCM-paper"]), "results/tables/e5_main_wilcoxon_vs_fcm.csv")
        save(guideline_table(df, "ASRFCM-paper", ["FIS-full", "FIS-split"], timing),
             "results/tables/e5_baseline_vs_improved.csv")
        save(guideline_table(df, "FCM", ["ASRFCM-paper"], timing), "results/tables/e5_fcm_vs_asrfcm.csv")
        for met in ("ACC", "NMI", "Iterations"):
            method_lines(s, "noise_pct", met, None, "image", MAIN_METHODS, str(FIGURES / f"e5_main_{met.lower()}"),
                         "mixed noise (%)")

    # ---- E6 BSDS (H2) ----
    df = load("e6_bsds_runs.csv")
    if df is not None:
        df["image"] = df["image"].str.replace("bsds:", "", regex=False)
        s = summarize(df, ["image"])
        paper = pd.read_csv(TABLES / "paper_reported_bsds.csv")
        paper["method"] = paper["method"].map({"FCM": "FCM", "Ours": "ASRFCM-paper"})
        paper["image"] = paper["image"].astype(str)
        s = s.merge(paper[["image", "method", "VPC", "ACC", "Kappa"]].rename(
            columns={"VPC": "VPC_paper", "ACC": "ACC_paper", "Kappa": "Kappa_paper_reported"}),
            on=["image", "method"], how="left")
        save(s, "results/tables/e6_bsds_summary.csv")
        save(paired_tests(df, ["image"], "ASRFCM-paper", ["FIS-full", "FIS-split"]), "results/tables/e6_bsds_wilcoxon.csv")
        means = df.groupby("method")[["ACC", "F", "NMI", "Kappa", "VPC", "VPE", "Iterations"]].mean().round(2)
        save(means.reset_index(), "results/tables/e6_bsds_mean_over_images.csv")
        save(guideline_table(df, "ASRFCM-paper", ["FIS-full", "FIS-split"], None), "results/tables/e6_bsds_baseline_vs_improved.csv")

    # ---- E5 FIS variants (H3, H4) ----
    df = load("e5_fis_variants_runs.csv")
    if df is not None:
        s = summarize(df, ["image", "noise_pct"])
        save(s, "results/tables/e5_fis_variants_summary.csv")
        others = [m for m in df.method.unique() if m != "ASRFCM-paper"]
        save(paired_tests(df, ["image", "noise_pct"], "ASRFCM-paper", others), "results/tables/e5_fis_variants_wilcoxon.csv")
        for ref, prefix in (("full tri centroid", "full"), ("split tri centroid", "split")):
            fam = [m for m in others if m.startswith(prefix) and m != ref]
            save(paired_tests(df, ["image", "noise_pct"], ref, fam), f"results/tables/e5_fis_variants_vs_{prefix}_ref.csv")

    # ---- E5 robustness (C1) ----
    df = load("e5_robustness_runs.csv")
    if df is not None:
        s = summarize(df, ["image", "noise_kind", "noise_pct"])
        save(s, "results/tables/e5_robustness_summary.csv")
        save(paired_tests(df, ["image", "noise_kind", "noise_pct"], "ASRFCM-paper", ["FCM", "FIS-full", "FIS-split"]),
             "results/tables/e5_robustness_wilcoxon.csv")
        method_lines(s, "noise_pct", "ACC", "noise_kind", "image", MAIN_METHODS, str(FIGURES / "e5_robustness_acc"),
                     "noise density (%)", row_order=["gaussian", "speckle", "salt_pepper", "mixed"])

    # ---- E5 ablation C2 ----
    df = load("e5_ablation_c2_runs.csv")
    if df is not None:
        s = summarize(df, ["image", "noise_pct"])
        save(s, "results/tables/e5_ablation_c2_summary.csv")
        others = [m for m in df.method.unique() if m != "paper"]
        save(paired_tests(df, ["image", "noise_pct"], "paper", others), "results/tables/e5_ablation_c2_wilcoxon.csv")

    # ---- E4 sensitivity (paper Figs. 10-13) ----
    df = load("e4_sensitivity_runs.csv")
    if df is not None:
        df = df[df.method != "paper"].copy()
        df["param"] = df.method.str.split("=").str[0]
        df["value"] = df.method.str.split("=").str[1].astype(float)
        df["method"] = df["image"]  # one line per image
        s = summarize(df, ["param", "value"])
        save(s.rename(columns={"method": "image"}), "results/tables/e4_sensitivity_summary.csv")
        for met in ("ACC", "VPC", "Iterations"):
            method_lines(s, "value", met, None, "param", ["sy1", "sy2", "sy3"],
                         str(FIGURES / f"e4_sensitivity_{met.lower()}"), "parameter value",
                         col_order=["sigma", "w", "k", "delta"], sharex=False)
    print("analysis done")


if __name__ == "__main__":
    main()
