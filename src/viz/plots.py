"""Plotting helpers shared by the experiment scripts (figures are always made from CSVs)."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

# Categorical slots 1-2 (blue, orange) of the validated default palette; identity is also
# carried by line style and marker, so the figure survives grayscale printing.
OURS = dict(color="#2a78d6", linestyle="-", marker="o", markersize=5, linewidth=2)
PAPER = dict(color="#eb6834", linestyle="--", marker="s", markersize=5, linewidth=2,
             markerfacecolor="white")
INK, MUTED, GRID = "#1f1f1e", "#6b6a63", "#e4e3dd"


SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]  # categorical slots 1-3 (one per image)
MARKERS = ["o", "s", "^"]


def ablation_dots(summary: pd.DataFrame, metrics: list[str], path_stem: str) -> None:
    """Dot plot per component combination: ours per image (coloured) vs paper-reported (black diamond)."""
    keys = ["local", "nonlocal", "sparse"]
    combos = summary[keys].drop_duplicates().sort_values(keys).values.tolist()
    labels = ["+".join(n for n, on in zip(("L", "NL", "S"), c) if on) or "none (FCM)" for c in combos]
    fig, axes = plt.subplots(1, len(metrics), figsize=(4.6 * len(metrics), 3.6), squeeze=False)
    for ax, met in zip(axes[0], metrics):
        for i, img in enumerate(sorted(summary.image.unique())):
            d = summary[summary.image == img]
            ys = [float(d[(d[keys] == c).all(axis=1)][f"{met}_mean"].iloc[0]) for c in combos]
            ax.plot(range(len(combos)), ys, linestyle="none", marker=MARKERS[i], markersize=7,
                    color=SERIES[i], label=f"{img} (ours, mean of 10 seeds)")
        d = summary[summary.image == summary.image.iloc[0]]
        ps = [float(d[(d[keys] == c).all(axis=1)][f"{met}_paper"].iloc[0]) for c in combos]
        ax.plot(range(len(combos)), ps, linestyle="none", marker="D", markersize=7, color=INK,
                markerfacecolor="white", label="paper-reported (Table 1)")
        ax.set_xticks(range(len(combos)))
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=8, color=INK)
        ax.set_ylabel(met if met == "Iterations" else f"{met} (%)", color=INK, fontsize=9)
        ax.grid(True, axis="y", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(colors=MUTED, labelsize=8)
    handles, lab = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, lab, loc="upper center", ncol=4, frameon=False, fontsize=8)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    for ext in ("png", "pdf"):
        fig.savefig(f"{path_stem}.{ext}", dpi=200)
    plt.close(fig)


def ours_vs_paper_grid(summary: pd.DataFrame, metrics: list[str], images: list[str],
                       method_label: str, path_stem: str) -> None:
    """Small multiples: rows = metrics, columns = images; x = noise level.

    `summary` needs columns image, noise_pct, metric, ours_mean, ours_std, paper_reported.
    Saves <path_stem>.png and <path_stem>.pdf.
    """
    fig, axes = plt.subplots(len(metrics), len(images), figsize=(3.2 * len(images), 2.6 * len(metrics)),
                             sharex=True, sharey="row", squeeze=False)
    for r, met in enumerate(metrics):
        for c, img in enumerate(images):
            ax = axes[r][c]
            d = summary[(summary.metric == met) & (summary.image == img)].sort_values("noise_pct")
            ax.errorbar(d.noise_pct, d.ours_mean, yerr=d.ours_std, capsize=3,
                        label=f"{method_label} (ours, mean ± std, 10 seeds)", **OURS)
            ax.plot(d.noise_pct, d.paper_reported, label=f"{method_label} (paper-reported)", **PAPER)
            ax.grid(True, color=GRID, linewidth=0.8)
            ax.set_axisbelow(True)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            for side in ("left", "bottom"):
                ax.spines[side].set_color(MUTED)
            ax.tick_params(colors=MUTED, labelsize=8)
            if r == 0:
                ax.set_title(img, color=INK, fontsize=10)
            if c == 0:
                ax.set_ylabel(met if met == "Iterations" else f"{met} (%)", color=INK, fontsize=9)
            if r == len(metrics) - 1:
                ax.set_xlabel("mixed noise (%)", color=INK, fontsize=9)
                ax.set_xticks(sorted(summary.noise_pct.unique()))
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    for ext in ("png", "pdf"):
        fig.savefig(f"{path_stem}.{ext}", dpi=200)
    plt.close(fig)
