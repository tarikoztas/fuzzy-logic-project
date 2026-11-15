"""Visual segmentation panels (seed 0): original, noisy, FCM, ASRFCM (paper), ASRFCM + FIS (full / split), ground truth.

Usage:  python experiments/plot_panels.py
Output: results/figures/panel_synthetic.{png,pdf}, results/figures/panel_bsds.{png,pdf}
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from experiments.run_grid import load_image, run_method  # noqa: E402
from src.data import noise  # noqa: E402
from src.eval.matching import match_labels  # noqa: E402

METHODS = [{"label": "FCM", "base": "FCM"}, {"label": "ASRFCM (paper)", "base": "paper"},
           {"label": "+FIS full", "base": "FIS-full (pre-registered)"},
           {"label": "+FIS split", "base": "FIS-split (post-hoc)"}]


def as_gray_levels(labels: np.ndarray, gt: np.ndarray, K: int) -> np.ndarray:
    """Show clusters with the gray level of their matched class, so panels are comparable."""
    matched, _ = match_labels(gt.ravel(), labels.ravel())
    return matched.reshape(gt.shape) / max(1, K - 1)


def panel(names: list[str], level: float, stem: str) -> None:
    cols = ["original", f"noisy ({level:g} %)"] + [m["label"] for m in METHODS] + ["ground truth"]
    fig, axes = plt.subplots(len(names), len(cols), figsize=(1.75 * len(cols), 1.45 * len(names) + 0.4),
                             squeeze=False)
    for i, name in enumerate(names):
        clean, gt, K = load_image(name)
        y = noise.add_noise(clean, "mixed", level / 100, 0)
        ims = [clean, y]
        for m in METHODS:
            res = run_method(y, K, 0, m)[0]  # (result, times, sigma_used)
            ims.append(as_gray_levels(res.labels, gt, K))
        ims.append(gt / max(1, K - 1))
        for j, im in enumerate(ims):
            ax = axes[i][j]
            ax.imshow(im, cmap="gray", vmin=0, vmax=1)
            ax.set_xticks([])
            ax.set_yticks([])
            if i == 0:
                ax.set_title(cols[j], fontsize=7)
            if j == 0:
                ax.set_ylabel(name.replace("bsds:", ""), fontsize=7)
    fig.tight_layout(pad=0.3)
    for ext in ("png", "pdf"):
        fig.savefig(f"{stem}.{ext}", dpi=200)
    plt.close(fig)
    print(f"saved {Path(stem).name}")


def main() -> None:
    out = ROOT / "results" / "figures"
    panel(["sy1", "sy2", "sy3"], 10, str(out / "panel_synthetic"))
    panel(["bsds:100007", "bsds:118035", "bsds:167062", "bsds:201080", "bsds:241004", "bsds:42049",
           "bsds:67079", "bsds:86016"], 5, str(out / "panel_bsds"))


if __name__ == "__main__":
    main()
