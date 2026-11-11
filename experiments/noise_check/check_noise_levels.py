"""Sanity check of our reading of the paper's "p % mixed noise" (D-027).

The paper does not define the noise level precisely. If our reading is close to
theirs, the *amount of damage* the noise does should be similar. We measure the
damage without any clustering algorithm: each noisy pixel is assigned to the
nearest TRUE gray level of the clean image ("oracle nearest-level classifier",
it knows the correct centers). Its ACC is printed next to the paper-reported
FCM ACC (Tables 2-8). FCM must estimate the centers, so it is usually a bit
worse than the oracle; the numbers should be of the same order, and the drop
with p should look alike. This is only a plausibility check, not a result.

Usage:  python experiments/noise_check/check_noise_levels.py
Output: results/tables/noise_oracle_check.csv
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.data import noise, synthetic
from src.eval.metrics import accuracy

ROOT = Path(__file__).resolve().parents[2]
LEVELS = (0.01, 0.05, 0.10, 0.15)
SEEDS = range(10)
# Paper-reported FCM ACC (%) from results/tables/paper_reported_fcm_vs_ours.csv
PAPER_FCM_ACC = {
    "sy1": (99.49, 95.20, 86.18, 77.97),
    "sy2": (97.82, 77.16, 67.75, 62.68),
    "sy3": (95.87, 74.75, 62.61, 57.45),
}


def oracle_labels(noisy: np.ndarray, levels: np.ndarray) -> np.ndarray:
    return np.argmin(np.abs(noisy[..., None] - levels), axis=-1)


def main() -> None:
    rows = []
    for name in synthetic.NAMES:
        s = synthetic.load(name)
        levels = np.asarray(synthetic.LEVELS[name]) / 255.0
        for i, p in enumerate(LEVELS):
            accs = [accuracy(s.labels, oracle_labels(noise.add_noise(s.image, "mixed", p, seed), levels))
                    for seed in SEEDS]
            rows.append({"image": name, "noise_pct": int(round(p * 100)),
                         "oracle_acc_mean": round(float(np.mean(accs)), 2),
                         "oracle_acc_std": round(float(np.std(accs)), 2),
                         "paper_fcm_acc": PAPER_FCM_ACC[name][i]})
    df = pd.DataFrame(rows)
    out = ROOT / "results" / "tables" / "noise_oracle_check.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(df.to_string(index=False))
    print(f"\nsaved {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
