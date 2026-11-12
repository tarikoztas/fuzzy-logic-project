"""Experiment E2: the paper's method (ASRFCM-CSI) on sy1-sy3 with mixed noise,
compared with the "Ours" column the paper reports (Tables 2-8), plus a
combined table with our FCM runs (E1).

Usage:
    python experiments/proposed/run_proposed.py --config experiments/proposed/config.yaml
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pandas as pd  # noqa: E402

from experiments.common import load_config, mean_abs_diff, save, summarize_vs_paper  # noqa: E402
from src.data import noise, synthetic  # noqa: E402
from src.eval.metrics import evaluate  # noqa: E402
from src.fcm.pipeline import run_asrfcm  # noqa: E402


def run(cfg: dict, method_label: str = "ASRFCM", fis=None) -> pd.DataFrame:
    rows = []
    mcfg = cfg["method"]
    for name in cfg["images"]:
        s = synthetic.load(name)
        for pct in cfg["noise"]["levels_pct"]:
            for seed in cfg["seeds"]:
                y = noise.add_noise(s.image, cfg["noise"]["kind"], pct / 100, seed)
                r = run_asrfcm(y, s.K, seed=seed, coeff_method=mcfg["coeff_method"],
                               coeff_variant=mcfg.get("coeff_variant", "signed"),
                               empty_col_policy=mcfg.get("empty_col_policy", "keep"), fis=fis,
                               **cfg.get("params", {}))
                m = evaluate(s.labels, U=r.result.U)
                rows.append({"method": method_label, "image": name, "noise_kind": cfg["noise"]["kind"],
                             "noise_pct": pct, "seed": seed, **m, "Iterations": r.result.n_iter,
                             **{f"time_{k}": v for k, v in r.times.items()}})
            print(f"{method_label} {name} {pct:>2}%: done", flush=True)
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=ROOT / "experiments" / "proposed" / "config.yaml")
    cfg = load_config(ap.parse_args().config)
    runs = run(cfg)
    save(runs, cfg["output"]["runs_csv"])
    summary = summarize_vs_paper(runs, "Ours")
    save(summary, cfg["output"]["summary_csv"])
    print("\nmean |ours - paper| per metric (paper 'Ours' column):")
    print(mean_abs_diff(summary).to_string())

    e1 = ROOT / "results" / "tables" / "e1_fcm_vs_paper.csv"
    if e1.exists():
        a = pd.read_csv(e1).assign(method="FCM")
        b = summary.assign(method="ASRFCM")
        save(pd.concat([a, b], ignore_index=True), cfg["output"]["combined_csv"])


if __name__ == "__main__":
    main()
