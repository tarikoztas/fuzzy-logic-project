"""Block diagram of the implemented system (paper method + both iterations of the fuzzy-rule extension).

Usage:  python experiments/plot_architecture.py
Output: results/figures/architecture.{png,pdf} (English) and architecture_tr.{png,pdf} (Turkish)
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
INK, MUTED = "#1f1f1e", "#6b6a63"
FILL = {"data": "#eef3fb", "paper": "#ffffff", "ours": "#fff1ea", "out": "#eaf7f1"}
EDGE = {"data": "#2a78d6", "paper": "#6b6a63", "ours": "#eb6834", "out": "#1baf7a"}

TEXT = {
    "en": dict(img="noisy gray\nimage y\nscaled to [0, 1]", sig="fuzzy σ (ours, it. 2)\nnoise estimate\n→ 3 rules → σ",
               xi="local information ξ\nreward/penalty sets\n(Alg. 2, Eqs. 5–9)", th="non-local information ϑ\nDTCWT → NLM on 7 bands\n→ inverse (Eqs. 10–11)",
               y="y (original value)", cf="coefficients α, β, γ\nclosed form\n(Eqs. 13–19)",
               fis="coefficients α, β, γ\nMamdani FIS (ours, it. 1)\nDev, Dis → 9 rules\n→ centroid",
               sfcm="sparse-regularised FCM\n(Alg. 3, Eqs. 20–29)\nd = α(y−c)²+β(ξ−c)²+γ(ϑ−c)²\nc → η → threshold √δ\n→ normalise → J",
               out="memberships U (K×N)\n→ defuzzify: argmax\n→ label map", paper="paper's method (reproduced)", ours="ours: replaces Eqs. 13–19"),
    "tr": dict(img="gürültülü gri\ngörüntü y\n[0, 1] aralığında", sig="bulanık σ (bizim, it. 2)\ngürültü tahmini\n→ 3 kural → σ",
               xi="yerel bilgi ξ\nödül/ceza kümeleri\n(Alg. 2, Denk. 5–9)", th="yerel-olmayan bilgi ϑ\nDTCWT → 7 bantta NLM\n→ ters dönüşüm (Denk. 10–11)",
               y="y (özgün değer)", cf="α, β, γ katsayıları\nkapalı form\n(Denk. 13–19)",
               fis="α, β, γ katsayıları\nMamdani FIS (bizim, it. 1)\nDev, Dis → 9 kural\n→ ağırlık merkezi",
               sfcm="seyrek düzenlileştirilmiş FCM\n(Alg. 3, Denk. 20–29)\nd = α(y−c)²+β(ξ−c)²+γ(ϑ−c)²\nc → η → eşik √δ\n→ normalize → J",
               out="üyelikler U (K×N)\n→ durulaştırma: argmax\n→ etiket haritası", paper="makalenin yöntemi (yeniden gerçekleştirildi)",
               ours="bizim: Denk. 13–19'un yerine"),
}


def box(ax, x, y, w, h, text, kind, fs=7.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.05",
                                facecolor=FILL[kind], edgecolor=EDGE[kind], linewidth=1.4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=INK)


def arrow(ax, x0, y0, x1, y1, style="-|>", color=INK, ls="-"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=9, color=color,
                                 linewidth=1.1, linestyle=ls))


def draw(lang: str) -> None:
    T = TEXT[lang]
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.6)
    ax.axis("off")
    box(ax, 0.05, 1.9, 1.6, 0.9, T["img"], "data")
    box(ax, 0.05, 3.3, 1.75, 0.95, T["sig"], "ours", fs=7)
    box(ax, 2.2, 3.3, 2.1, 0.95, T["xi"], "paper")
    box(ax, 2.2, 1.95, 2.1, 0.95, T["th"], "paper", fs=6.8 if lang == "tr" else 7.2)
    box(ax, 2.2, 0.35, 2.1, 0.95, T["y"], "data")
    box(ax, 4.9, 3.3, 2.0, 0.95, T["cf"], "paper")
    box(ax, 4.9, 1.75, 2.0, 1.15, T["fis"], "ours", fs=7.2)
    box(ax, 7.4, 1.95, 2.45, 1.4, T["sfcm"], "paper", fs=7.2)
    box(ax, 7.4, 0.3, 2.45, 1.0, T["out"], "out")
    for yy in (3.55, 2.42, 0.82):
        arrow(ax, 1.6, 2.35, 2.2, yy)
    arrow(ax, 0.85, 2.8, 0.85, 3.3, color=EDGE["ours"])
    arrow(ax, 1.8, 3.95, 2.2, 3.95, color=EDGE["ours"])
    arrow(ax, 4.3, 3.78, 4.9, 3.78)
    arrow(ax, 4.3, 2.42, 4.9, 2.42)
    arrow(ax, 4.3, 3.6, 4.9, 2.7, color=EDGE["ours"])
    arrow(ax, 4.3, 1.05, 4.9, 1.85, color=EDGE["ours"])
    arrow(ax, 6.9, 3.78, 7.4, 3.1)
    arrow(ax, 6.9, 2.32, 7.4, 2.5, color=EDGE["ours"])
    arrow(ax, 8.62, 1.95, 8.62, 1.3)
    ax.text(5.9, 4.42, T["paper"], ha="center", fontsize=7.5, color=EDGE["paper"])
    ax.text(6.95, 1.45, T["ours"], ha="right", fontsize=7.2, color=EDGE["ours"])
    fig.tight_layout(pad=0.2)
    out = ROOT / "results" / "figures" / ("architecture" + ("" if lang == "en" else "_tr"))
    for ext in ("png", "pdf"):
        fig.savefig(f"{out}.{ext}", dpi=220)
    plt.close(fig)
    print(f"saved {out.relative_to(ROOT)}.png/.pdf")


def main() -> None:
    for lang in ("en", "tr"):
        draw(lang)


if __name__ == "__main__":
    main()
