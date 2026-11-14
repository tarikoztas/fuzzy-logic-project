"""Analysis of the second iteration (E8, D-044/D-045): summaries, paired Wilcoxon tests,
the verdicts of the pre-registered hypotheses H5, H5-control and H6, and figures.

Every number comes from the test-run CSVs written by experiments/run_grid.py with
experiments/contribution/{second_iteration,robustness_second,bsds_second,bsds_rgb_second}.yaml.
The hypothesis checks below implement the criteria of D-045 / CP6 part 2 literally.

Usage:  python experiments/analyze_second_iteration.py
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
import pandas as pd  # noqa: E402
from scipy.stats import wilcoxon  # noqa: E402

from experiments.analyze_contribution import guideline_table, paired_tests, summarize  # noqa: E402
from experiments.common import FIGURES, TABLES, save  # noqa: E402
from src.viz.plots import GRID, INK, MUTED, SERIES, method_lines  # noqa: E402

PAPER, FIXED, FS, FSA = "ASRFCM-paper", "sigma=0.9 (fixed)", "FIS-sigma", "FIS-sigma+A"
PLOT_METHODS = [PAPER, FIXED, FS, FSA, "FIS-full"]
XLABEL = {"en": "mixed noise (%)", "tr": "karışık gürültü (%)"}
XLABEL_ROB = {"en": "noise density (%)", "tr": "gürültü yoğunluğu (%)"}
# display names in the figures (the CSVs keep the method labels of the configs)
SHOW = {"en": {PAPER: "ASRFCM (σ = 0.3)", FIXED: "σ = 0.9 fixed", FS: "FIS-σ", FSA: "FIS-σ+A", "FIS-full": "FIS-full"},
        "tr": {PAPER: "ASRFCM (σ = 0.3)", FIXED: "σ = 0.9 sabit", FS: "FIS-σ", FSA: "FIS-σ+A", "FIS-full": "FIS-full"}}
KIND = {"en": {"gaussian": "Gaussian", "speckle": "speckle", "salt_pepper": "salt-and-pepper", "mixed": "mixed"},
        "tr": {"gaussian": "Gauss", "speckle": "benek", "salt_pepper": "tuz-biber", "mixed": "karışık"}}


def load(name: str) -> pd.DataFrame | None:
    p = TABLES / name
    return pd.read_csv(p) if p.exists() else None


def pooled_test(df: pd.DataFrame, level: int, base: str, other: str) -> dict:
    """Paired two-sided Wilcoxon over all image-seed pairs at one noise level (n = 30)."""
    g = df[df.noise_pct == level]
    a = g[g.method == base].set_index(["image", "seed"]).ACC
    b = g[g.method == other].set_index(["image", "seed"]).ACC
    common = a.index.intersection(b.index)
    d = (b[common] - a[common]).values
    p = 1.0 if np.allclose(d, 0) else float(wilcoxon(d, zero_method="zsplit").pvalue)
    return {"noise_pct": level, "method": other, "baseline": base, "n": len(d),
            "mean_diff": round(float(d.mean()), 3), "p_value": float(f"{p:.3g}"), "significant_0.05": p < 0.05}


def hypotheses(df: pd.DataFrame) -> pd.DataFrame:
    acc = df.groupby(["image", "noise_pct", "method"]).ACC.mean().unstack("method")
    pooled = {(lvl, b, o): pooled_test(df, lvl, b, o) for lvl in (1, 5, 10, 15)
              for b, o in ((PAPER, FS), (FIXED, FS), (PAPER, FSA))}
    rows = []
    # H5 (a): higher at 10 and 15 %, each significant (pooled n = 30)
    a_ok = all(pooled[(l, PAPER, FS)]["mean_diff"] > 0 and pooled[(l, PAPER, FS)]["significant_0.05"] for l in (10, 15))
    # H5 (b): at 1 and 5 % not more than 0.5 point lower on any image
    low = (acc[FS] - acc[PAPER]).loc[(slice(None), [1, 5])]
    b_ok = bool((low >= -0.5).all())
    rows.append({"hypothesis": "H5", "criterion": "FIS-sigma > paper at 10 % and 15 % (pooled Wilcoxon p<0.05)",
                 "value": "; ".join(f"{l}%: {pooled[(l, PAPER, FS)]['mean_diff']:+.2f} (p={pooled[(l, PAPER, FS)]['p_value']:.1e})"
                                    for l in (10, 15)), "holds": a_ok})
    rows.append({"hypothesis": "H5", "criterion": "FIS-sigma not >0.5 below paper at 1 % and 5 % on any image",
                 "value": f"worst {low.min():+.2f}", "holds": b_ok})
    rows.append({"hypothesis": "H5", "criterion": "overall", "value": "", "holds": a_ok and b_ok})
    # H5-control: |FIS-sigma - fixed 0.9| < 0.5 on every synthetic mixed-noise setting
    dc = (acc[FS] - acc[FIXED])
    rows.append({"hypothesis": "H5-control", "criterion": "|FIS-sigma - sigma 0.9| < 0.5 on every setting (expected null)",
                 "value": f"range {dc.min():+.2f} to {dc.max():+.2f}", "holds": bool((dc.abs() < 0.5).all())})
    # H6: FIS-sigma+A >= paper at every level on every image, no significant loss
    d6 = acc[FSA] - acc[PAPER]
    per = paired_tests(df, ["image", "noise_pct"], PAPER, [FSA])
    sig_loss = per[(per.mean_diff < 0) & per["significant_0.05"]]
    rows.append({"hypothesis": "H6", "criterion": "FIS-sigma+A mean ACC >= paper on every image and level",
                 "value": f"worst {d6.min():+.2f}", "holds": bool((d6 >= 0).all())})
    rows.append({"hypothesis": "H6", "criterion": "no significant loss (per image and level, p<0.05)",
                 "value": f"{len(sig_loss)} significant losses", "holds": sig_loss.empty})
    rows.append({"hypothesis": "H6", "criterion": "overall", "value": "",
                 "holds": bool((d6 >= 0).all()) and sig_loss.empty})
    return pd.DataFrame(rows), pd.DataFrame(pooled.values())


def sigma_fis_figure(stem: str, lang: str, marks: dict[str, float]) -> None:
    """Membership functions of the sigma FIS and its input-output curve, with measured noise levels."""
    from src.fcm.fis_sigma import build_sigma_fis
    from src.fcm.variants import FIS_SIGMA

    fis = build_sigma_fis(FIS_SIGMA["breaks"], FIS_SIGMA["out"])
    inp, out = fis.inputs[0], fis.outputs[0]
    T = {"en": dict(a="Input: image noise estimate", b="Output: reward factor σ", c="Rule base → σ",
                    x="median(|HH|) / 0.6745", y="membership", s="σ", terms={}),
         "tr": dict(a="Girdi: görüntü gürültü tahmini", b="Çıktı: ödül katsayısı σ", c="Kural tabanı → σ",
                    x="median(|HH|) / 0.6745", y="üyelik derecesi", s="σ",
                    terms={"Low": "Düşük", "Medium": "Orta", "High": "Yüksek", "Small": "Küçük", "Large": "Büyük"})}[lang]
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.0))
    x = np.linspace(*inp.universe, 401)
    for k, (t, mf) in enumerate(inp.terms.items()):
        axes[0].plot(x, mf(x), color=SERIES[k], linestyle=["-", "--", "-."][k], lw=2, label=T["terms"].get(t, t))
    z = np.linspace(0, 1.2, 481)
    for k, (t, mf) in enumerate(out.terms.items()):
        axes[1].plot(z, mf(z), color=SERIES[k], linestyle=["-", "--", "-."][k], lw=2, label=T["terms"].get(t, t))
    s = fis.evaluate(Noise=x)["Sigma"]
    axes[2].plot(x, np.clip(s, 0, 0.95), color=SERIES[0], lw=2)
    prev, ylab = -1.0, 0.27
    for name, v in sorted(marks.items(), key=lambda kv: kv[1]):
        for ax in (axes[0], axes[2]):
            ax.axvline(v, color=MUTED, lw=0.8, ls=":")
        ylab = ylab + 0.2 if v - prev < 0.02 else 0.27   # stagger labels of close marks
        axes[2].annotate(name, (v, ylab), rotation=90, fontsize=7, color=MUTED, ha="right", va="bottom")
        prev = v
    axes[0].set(title=T["a"], xlabel=T["x"], ylabel=T["y"])
    axes[1].set(title=T["b"], xlabel=T["s"], xlim=(0, 1.2))
    axes[2].set(title=T["c"], xlabel=T["x"], ylabel=T["s"], ylim=(0.25, 1.0))
    for ax in axes:
        ax.grid(True, color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.title.set_fontsize(9.5); ax.title.set_color(INK)
        ax.tick_params(labelsize=8, colors=MUTED)
    for ax in axes[:2]:
        ax.set_ylim(-0.03, 1.32)
        ax.legend(fontsize=8, frameon=False, loc="upper center", ncol=3, handlelength=2.2)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(f"{stem}.{ext}", dpi=200)
    plt.close(fig)


def measured_noise_levels() -> dict[str, float]:
    """Noise estimate of sy2 at each test level (seed 0) and the median over the 8 BSDS500 images at 5 %."""
    from src.data import bsds500, noise, synthetic
    from src.fcm.fis_sigma import noise_estimate

    marks = {}
    s = synthetic.load("sy2")
    for p in (1, 5, 10, 15):
        marks[f"sy2 {p}%"] = noise_estimate(noise.add_noise(s.image, "mixed", p / 100, 0))
    try:
        v = [noise_estimate(noise.add_noise(bsds500.load(pid).gray, "mixed", 0.05, 0)) for pid in bsds500.PAPER_IDS]
        marks["BSDS 5%"] = float(np.median(v))
    except Exception:  # BSDS500 images not downloaded (clean clone): figure without that mark
        pass
    return marks


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    timing = load("e7_timing.csv")

    df = load("e8_second_iteration_runs.csv")
    if df is not None:
        s = summarize(df, ["image", "noise_pct"])
        save(s, "results/tables/e8_second_iteration_summary.csv")
        others = [m for m in df.method.unique() if m != PAPER]
        save(paired_tests(df, ["image", "noise_pct"], PAPER, others), "results/tables/e8_second_iteration_wilcoxon.csv")
        save(paired_tests(df, ["image", "noise_pct"], FIXED, [FS, FSA]), "results/tables/e8_second_iteration_vs_fixed.csv")
        hyp, pooled = hypotheses(df)
        save(hyp, "results/tables/e8_hypotheses.csv")
        save(pooled, "results/tables/e8_pooled_wilcoxon.csv")
        save(guideline_table(df, PAPER, [FS, FSA], timing), "results/tables/e8_baseline_vs_improved.csv")
        print(hyp.to_string(index=False))
        sig = df.groupby(["noise_pct", "method"]).sigma_used.mean().unstack() if "sigma_used" in df else None
        if sig is not None:
            print("\nmean sigma used\n", sig.round(3).to_string())
        for lang in ("en", "tr"):
            suf = "" if lang == "en" else "_tr"
            sl = s.assign(method=s.method.map(lambda m: SHOW[lang].get(m, m)))
            method_lines(sl, "noise_pct", "ACC", None, "image", [SHOW[lang][m] for m in PLOT_METHODS],
                         str(FIGURES / f"e8_main_acc{suf}"), XLABEL[lang])

    for name, tag in (("e8_bsds_second_runs.csv", "bsds:"), ("e8_bsds_rgb_second_runs.csv", "bsdsrgb:")):
        df = load(name)
        if df is None:
            continue
        df["image"] = df["image"].str.replace(tag, "", regex=False)
        stem = name.replace("_runs.csv", "")
        save(summarize(df, ["image"]), f"results/tables/{stem}_summary.csv")
        save(paired_tests(df, ["image"], PAPER, [FIXED, FS, FSA]), f"results/tables/{stem}_wilcoxon.csv")
        save(paired_tests(df, ["image"], FIXED, [FS]), f"results/tables/{stem}_vs_fixed.csv")
        means = df.groupby("method")[["ACC", "F", "NMI", "VPC", "Iterations"]].mean().round(2)
        save(means.reset_index(), f"results/tables/{stem}_mean_over_images.csv")
        if "sigma_used" in df:
            print(stem, "sigma per image:", df[df.method == FS].groupby("image").sigma_used.mean().round(3).to_dict())
        print(stem, means.ACC.to_dict())

    df = load("e8_robustness_second_runs.csv")
    if df is not None:
        s = summarize(df, ["image", "noise_kind", "noise_pct"])
        save(s, "results/tables/e8_robustness_second_summary.csv")
        save(paired_tests(df, ["image", "noise_kind", "noise_pct"], PAPER, [FIXED, FS, FSA]),
             "results/tables/e8_robustness_second_wilcoxon.csv")
        save(paired_tests(df, ["image", "noise_kind", "noise_pct"], FIXED, [FS]),
             "results/tables/e8_robustness_second_vs_fixed.csv")
        for lang in ("en", "tr"):
            suf = "" if lang == "en" else "_tr"
            sl = s.assign(method=s.method.map(lambda m: SHOW[lang].get(m, m)), noise_kind=s.noise_kind.map(KIND[lang]))
            method_lines(sl, "noise_pct", "ACC", "noise_kind", "image", [SHOW[lang][m] for m in (PAPER, FIXED, FS, FSA)],
                         str(FIGURES / f"e8_robustness_acc{suf}"), XLABEL_ROB[lang],
                         row_order=[KIND[lang][k] for k in ("gaussian", "speckle", "salt_pepper", "mixed")])

    marks = measured_noise_levels()
    for lang in ("en", "tr"):
        sigma_fis_figure(str(FIGURES / ("e8_sigma_fis" + ("" if lang == "en" else "_tr"))), lang, marks)
    print("figures saved")


if __name__ == "__main__":
    main()
