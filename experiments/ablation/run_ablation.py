"""Experiment E3: component ablation (paper Table 1) — local / non-local / sparse on or off.

Usage:
    python experiments/ablation/run_ablation.py --config experiments/ablation/config.yaml
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402

from experiments.common import TABLES, load_config, save  # noqa: E402
from src.data import noise, synthetic  # noqa: E402
from src.eval.metrics import evaluate  # noqa: E402
from src.fcm.pipeline import run_asrfcm  # noqa: E402

METRICS = ["VPC", "VPE", "ACC", "F", "NMI", "Kappa", "Kappa_paper", "Iterations"]


def run(cfg: dict) -> pd.DataFrame:
    rows = []
    pct = cfg["noise"]["level_pct"]
    for name in cfg["images"]:
        s = synthetic.load(name)
        for seed in cfg["seeds"]:
            y = noise.add_noise(s.image, cfg["noise"]["kind"], pct / 100, seed)
            for loc, nl, sp in cfg["combinations"]:
                r = run_asrfcm(y, s.K, seed=seed, use_local=bool(loc), use_nonlocal=bool(nl),
                               use_sparse=bool(sp), coeff_variant=cfg["method"]["coeff_variant"],
                               empty_col_policy=cfg["method"]["empty_col_policy"])
                m = evaluate(s.labels, U=r.result.U)
                rows.append({"image": name, "noise_pct": pct, "seed": seed, "local": loc, "nonlocal": nl,
                             "sparse": sp, **m, "Iterations": r.result.n_iter})
        print(f"{name}: done", flush=True)
    return pd.DataFrame(rows)


def summarize(runs: pd.DataFrame) -> pd.DataFrame:
    paper = pd.read_csv(TABLES / "paper_reported_ablation.csv").rename(columns={"Fscore": "F"})
    keys = ["local", "nonlocal", "sparse"]
    out = []
    for (name, *combo), g in runs.groupby(["image", *keys]):
        prow = paper[(paper[keys] == combo).all(axis=1)].iloc[0]
        row = {"image": name, **dict(zip(keys, combo))}
        for met in METRICS:
            row[f"{met}_mean"] = round(float(g[met].mean()), 2)
            row[f"{met}_std"] = round(float(g[met].std(ddof=0)), 2)
            pname = "Kappa" if met == "Kappa_paper" else met
            row[f"{met}_paper"] = float(prow[pname]) if met != "Kappa" else float("nan")
        out.append(row)
    return pd.DataFrame(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=ROOT / "experiments" / "ablation" / "config.yaml")
    cfg = load_config(ap.parse_args().config)
    runs = run(cfg)
    save(runs, cfg["output"]["runs_csv"])
    summary = summarize(runs)
    save(summary, cfg["output"]["summary_csv"])
    cols = ["image", "local", "nonlocal", "sparse", "VPC_mean", "VPC_paper", "ACC_mean", "ACC_paper",
            "Iterations_mean", "Iterations_paper"]
    print(summary[cols].to_string(index=False))


if __name__ == "__main__":
    main()
