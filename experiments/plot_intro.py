"""Introductory figure for the slides: what noisy image segmentation is (seed 0).

Two rows (synthetic sy3 with 10 % mixed noise, BSDS500 image 42049 with 5 % mixed noise),
columns: noisy input, FCM, the reference method with the paper's settings, ground truth.

Usage:  python experiments/plot_intro.py
Output: results/figures/intro_segmentation.png and intro_segmentation_tr.png (Turkish labels)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from experiments.plot_panels import as_gray_levels  # noqa: E402
from experiments.run_grid import load_image, run_method  # noqa: E402
from src.data import noise  # noqa: E402

ROWS = [("sy3", 10), ("bsds:42049", 5)]
LABELS = {"en": ["noisy input", "FCM", "reference method", "ground truth"],
          "tr": ["gürültülü girdi", "FCM", "referans yöntem", "doğru bölütleme"]}


def main() -> None:
    panels = []
    for name, level in ROWS:
        clean, gt, K = load_image(name)
        y = noise.add_noise(clean, "mixed", level / 100, 0)
        fcm = run_method(y, K, 0, {"base": "FCM"})[0]
        ref = run_method(y, K, 0, {"base": "paper"})[0]
        panels.append((name, level, [y, as_gray_levels(fcm.labels, gt, K), as_gray_levels(ref.labels, gt, K), gt / max(1, K - 1)]))
    for lang, cols in LABELS.items():
        fig, axes = plt.subplots(len(panels), 4, figsize=(8.0, 4.3), squeeze=False)
        for i, (name, level, ims) in enumerate(panels):
            for j, im in enumerate(ims):
                ax = axes[i][j]
                ax.imshow(im, cmap="gray", vmin=0, vmax=1)
                ax.set_xticks([]); ax.set_yticks([])
                if i == 0:
                    ax.set_title(cols[j], fontsize=10)
                if j == 0:
                    tag = name.replace("bsds:", "BSDS500 ")
                    ax.set_ylabel(f"{tag}, {level} %" if lang == "en" else f"{tag}, %{level}", fontsize=9)
        fig.tight_layout(pad=0.4)
        out = ROOT / "results" / "figures" / f"intro_segmentation{'' if lang == 'en' else '_tr'}.png"
        fig.savefig(out, dpi=200)
        plt.close(fig)
        print(f"saved {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
