"""Experiment E7: run time per image size and method, single process, no cache.

Pre-processing (xi, theta, coefficients) and clustering are timed separately.
Run it on an otherwise idle machine; other experiments run in parallel and their
times are not used for timing claims.

Usage:  python experiments/timing/run_timing.py
Output: results/tables/e7_timing.csv, e7_timing_summary.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import cv2  # noqa: E402
import pandas as pd  # noqa: E402

from experiments.common import save  # noqa: E402
from experiments.run_grid import run_method  # noqa: E402
from src.data import bsds500, noise, synthetic  # noqa: E402
from src.fcm.pipeline import run_asrfcm  # noqa: E402

METHODS = [{"label": "FCM", "base": "FCM"}, {"label": "ASRFCM-paper", "base": "paper"},
           {"label": "FIS-full", "base": "FIS-full (pre-registered)"},
           {"label": "FIS-split", "base": "FIS-split (post-hoc)"},
           {"label": "FIS-sigma", "base": "FIS-sigma"}, {"label": "FIS-sigma+A", "base": "FIS-sigma+A"}]
REPEATS = 3


def images():
    s = synthetic.load("sy3")
    yield "sy3 128x128", cv2.resize(s.image, (128, 128), interpolation=cv2.INTER_NEAREST), 3
    yield "sy3 256x256", s.image, 3
    yield "BSDS 321x481 (42049)", bsds500.load("42049").gray, 2


def main() -> None:
    # warm-up (imports, first allocation) not timed
    s = synthetic.load("sy1")
    run_asrfcm(noise.add_noise(s.image, "mixed", 0.05, 0), 2, use_cache=False)
    rows = []
    for name, img, K in images():
        y = noise.add_noise(img, "mixed", 0.05, 0)
        for m in METHODS:
            for r in range(REPEATS):
                res, t, _sigma = run_method_nocache(y, K, m)
                pre = t.get("xi_s", 0) + t.get("theta_s", 0) + t.get("coeff_s", 0)
                rows.append({"image": name, "pixels": y.size, "method": m["label"], "repeat": r,
                             "preprocess_s": pre, "cluster_s": t["cluster_s"], "total_s": pre + t["cluster_s"],
                             "iterations": res.n_iter, **t})
            print(f"{name} {m['label']}: done", flush=True)
    df = pd.DataFrame(rows)
    save(df, "results/tables/e7_timing.csv")
    summ = df.groupby(["image", "pixels", "method"])[["preprocess_s", "cluster_s", "total_s", "iterations"]].mean()
    save(summ.round(3).reset_index(), "results/tables/e7_timing_summary.csv")
    print(summ.round(3).to_string())


def run_method_nocache(y, K, m):
    """run_method with the xi/theta cache disabled, so pre-processing is really computed."""
    from src.fcm import pipeline

    orig = pipeline.run_asrfcm

    def nocache(*a, **kw):
        kw["use_cache"] = False
        return orig(*a, **kw)

    pipeline.run_asrfcm = nocache
    try:
        return run_method(y, K, 0, m)
    finally:
        pipeline.run_asrfcm = orig


if __name__ == "__main__":
    main()
