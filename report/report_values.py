"""All numbers and tables used in the report and in README.md, computed from results/tables/*.csv.

compute(lang) returns the values for the English ("en") or the Turkish ("tr") report: the
numbers are identical, only captions, column names and sentences change (L(en, tr)).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"
sys.path.insert(0, str(ROOT))

from report.build_report import html_table, mean_std  # noqa: E402

SY = ["sy1", "sy2", "sy3"]
LANG = {"value": "en"}


def L(en: str, tr: str) -> str:
    """Pick the text of the current report language."""
    return tr if LANG["value"] == "tr" else en


def csv(name: str) -> pd.DataFrame:
    return pd.read_csv(TABLES / name)


def mad(summary: pd.DataFrame, metric: str, cond=None) -> tuple[float, float]:
    s = summary[(summary.metric == metric) & summary.paper_reported.notna()]
    if cond is not None:
        s = s[cond(s)]
    d = s.diff_ours_minus_paper.abs()
    return float(d.mean()), float(d.max())


def md_table(df: pd.DataFrame) -> str:
    head = "| " + " | ".join(map(str, df.columns)) + " |\n|" + "---|" * len(df.columns) + "\n"
    return head + "\n".join("| " + " | ".join(map(str, r)) + " |" for r in df.values)


def count_tests() -> int:
    out = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q"], cwd=ROOT,
                         capture_output=True, text=True).stdout
    import re
    per_file = re.findall(r"^tests/\S+\.py: (\d+)$", out, re.M)   # pytest.ini adds -q -> "-qq" summary per file
    if per_file:
        return sum(map(int, per_file))
    m = re.search(r"(\d+) tests? collected", out)
    if not m:
        raise RuntimeError("could not count the unit tests")
    return int(m.group(1))


def compute(lang: str = "en") -> tuple[dict, dict]:
    LANG["value"] = lang
    V: dict[str, str] = {}
    readme: dict[str, str] = {}

    # ---------- E1 / E2 ----------
    e1 = csv("e1_fcm_vs_paper.csv")
    e2 = csv("e2_asrfcm_vs_paper.csv")
    m, x = mad(e1, "ACC")
    V["E1_acc_mad"], V["E1_acc_max"] = f"{m:.2f}", f"{x:.2f}"
    for met in ("NMI", "VPC", "VPE", "F", "Kappa_paper"):
        V[f"E1_{met}_mad"] = f"{mad(e1, met)[0]:.2f}"
    it = e1[e1.metric == "Iterations"]
    V["E1_iter_diff"] = f"{(it.paper_reported - it.ours_mean).mean():.1f}"
    m, x = mad(e2, "ACC")
    V["E2_acc_mad"], V["E2_acc_max"] = f"{m:.2f}", f"{x:.2f}"
    V["E2_acc_mad_low"] = f"{mad(e2, 'ACC', lambda s: s.noise_pct <= 5)[0]:.2f}"
    V["E2_acc_mad_high"] = f"{mad(e2, 'ACC', lambda s: s.noise_pct >= 10)[0]:.2f}"
    acc = e2[e2.metric == "ACC"].set_index(["image", "noise_pct"])
    gaps = (acc.paper_reported - acc.ours_mean)
    V["E2_acc_maxgap"] = f"{gaps.max():.1f}"
    for met in ("NMI", "VPC", "VPE"):
        V[f"E2_{met}_mad"] = f"{mad(e2, met)[0]:.2f}"
    e1a = e1[e1.metric == "ACC"].set_index(["image", "noise_pct"])
    V["E2_max_gain_over_fcm"] = f"{(acc.ours_mean - e1a.ours_mean).max():.1f}"
    rows = []
    for img in SY:
        for p in (1, 5, 10, 15):
            a1, a2 = e1a.loc[(img, p)], acc.loc[(img, p)]
            rows.append([img, p, f2s(a1.ours_mean), f2s(a1.paper_reported), f2s(a2.ours_mean), f2s(a2.paper_reported)])
    t = pd.DataFrame(rows, columns=[L("Image", "Görüntü"), L("Noise %", "Gürültü %"), L("FCM ours", "FCM bizim"),
                                    L("FCM paper", "FCM makale"), L("ASRFCM ours", "ASRFCM bizim"),
                                    L("ASRFCM paper", "ASRFCM makale")])
    V["TABLE_e2"] = html_table(t, L("Table III. ACC (%) on the synthetic images: ours (mean of 10 seeds) vs paper-reported (Table 4 of [1])",
                                    "Tablo III. Sentetik görüntülerde ACC (%): bizim (10 tohumun ortalaması) ve makalede raporlanan ([1], Tablo 4)"),
                               left_cols=1)
    readme["reproduction"] = ("**E1/E2 — ACC (%) on the synthetic images, ours (mean of 10 seeds) vs paper-reported:**\n\n" + md_table(t)
                              + f"\n\nMean |ours − paper| ACC: FCM {V['E1_acc_mad']} points; ASRFCM {V['E2_acc_mad_low']} points up to 5 % noise and "
                              f"{V['E2_acc_mad_high']} points at 10–15 %. Figures: `results/figures/e1_fcm_vs_paper.png`, `e2_asrfcm_vs_paper.png`.")

    # ---------- E3 ----------
    e3 = csv("e3_ablation_vs_paper.csv")
    lab = lambda r: "+".join(n for n, on in zip(("L", "NL", "S"), (r["local"], r["nonlocal"], r["sparse"])) if on) or L("none (FCM)", "yok (FCM)")
    rows = []
    for _, r in e3[e3.image == "sy3"].iterrows():
        rows.append([lab(r), f2s(r.ACC_mean), f2s(r.ACC_paper), f2s(r.VPC_mean), f2s(r.VPC_paper), f"{r.Iterations_mean:.1f}", f"{r.Iterations_paper:.0f}"])
    t3 = pd.DataFrame(rows, columns=[L("Components", "Bileşenler"), L("ACC ours", "ACC bizim"), L("ACC paper", "ACC makale"),
                                     L("V_PC ours", "V_PC bizim"), L("V_PC paper", "V_PC makale"), L("Iter. ours", "İter. bizim"),
                                     L("Iter. paper", "İter. makale")])
    V["TABLE_e3"] = html_table(t3, L("Table IV. Ablation on sy3, 5 % noise (L local, NL non-local, S sparse); paper values from its Table 1 (image not named)",
                                     "Tablo IV. sy3 üzerinde ablasyon, %5 gürültü (L yerel, NL yerel-olmayan, S seyrek); makale değerleri Tablo 1'den (görüntü belirtilmemiş)"))
    full = e3[(e3.local == 1) & (e3["nonlocal"] == 1) & (e3["sparse"] == 1)].set_index("image")
    V["E3_full_acc"] = " / ".join(f2s(full.loc[i, "ACC_mean"]) for i in SY)
    lo = e3[(e3.local == 1) & (e3["nonlocal"] == 0) & (e3["sparse"] == 0)].set_index("image")
    V["E3_local_only"] = f"{lo.ACC_mean.min():.1f}–{lo.ACC_mean.max():.1f}"
    nl = e3[(e3.local == 0) & (e3["nonlocal"] == 1) & (e3["sparse"] == 0)].set_index("image")
    V["E3_nl_only"] = f"{nl.ACC_mean.min():.1f}–{nl.ACC_mean.max():.1f}"

    # ---------- E5 main ----------
    d5 = csv("e5_main_runs.csv")
    w5 = csv("e5_main_wilcoxon.csv")
    piv = d5.pivot_table(index=["image", "noise_pct"], columns="method", values="ACC")
    sub = piv.loc[[("sy2", 15), ("sy3", 15)]]
    drop_full = sub["ASRFCM-paper"] - sub["FIS-full"]
    V["E5_full_acc_drop15"] = f"{drop_full.min():.1f}–{drop_full.max():.1f}"
    drop_split = sub["ASRFCM-paper"] - sub["FIS-split"]
    V["E5_split_acc_drop15"] = f"{drop_split.min():.1f}–{drop_split.max():.1f}"
    rows = []
    for img in SY:
        for p in (1, 5, 10, 15):
            g = d5[(d5.image == img) & (d5.noise_pct == p)]
            r = [img, p]
            for mth in ("FCM", "ASRFCM-paper", "FIS-full", "FIS-split"):
                r.append(mean_std(g[g.method == mth].ACC))
            for mth in ("FIS-full", "FIS-split"):
                ww = w5[(w5.image == img) & (w5.noise_pct == p) & (w5.method == mth)].iloc[0]
                r.append(f"{ww.mean_diff:+.2f}{'*' if ww['significant_0.05'] else ''}")
            rows.append(r)
    t5 = pd.DataFrame(rows, columns=[L("Image", "Görüntü"), L("Noise %", "Gürültü %"), "FCM",
                                     L("ASRFCM (paper coeff.)", "ASRFCM (makale katsayıları)"), "+FIS full", "+FIS split",
                                     "Δ full", "Δ split"])
    V["TABLE_e5"] = html_table(t5, L("Table VI. ACC (%) of the extension, mean ± std over 10 seeds; Δ = difference to ASRFCM with the paper's coefficients; * paired Wilcoxon p < 0.05",
                                     "Tablo VI. Geliştirmenin ACC değerleri (%), 10 tohumda ortalama ± std; Δ = makale katsayılı ASRFCM'ye göre fark; * eşleştirilmiş Wilcoxon p < 0.05"),
                               wide=True)
    gl = pd.read_csv(TABLES / "e5_baseline_vs_improved.csv", dtype=str)
    gl["Metric"] = gl["Metric"].replace({"Kappa": L("Kappa (Cohen)", "Kappa (Cohen)"),
                                         "Kappa_paper": L("Kappa (paper's definition)", "Kappa (makalenin tanımı)"),
                                         "VPC": "V_PC", "VPE": "V_PE",
                                         "Iterations": L("Iterations", "İterasyon"),
                                         "Time per 256x256 image (s, E7)": L("Time per 256x256 image (s, E7)", "256×256 görüntü başına süre (s, E7)")})
    if lang == "tr":
        gl.columns = [c.replace("Metric", "Ölçüt").replace("Baseline", "Temel").replace("Improved", "Geliştirilen")
                      .replace("Change", "Değişim") for c in gl.columns]
    V["TABLE_guideline"] = html_table(gl, L("Table VII. Baseline vs improved over all synthetic settings (12 settings × 10 seeds; guideline format)",
                                            "Tablo VII. Tüm sentetik ayarlarda temel ve geliştirilen yöntem (12 ayar × 10 tohum; yönerge biçimi)"),
                                      wide=True)
    sig_pos = w5[(w5.mean_diff > 0) & w5["significant_0.05"]]
    V["E5_sig_gains"] = "; ".join(
        L(f"{r.method} on {r.image} at {r.noise_pct} % ({r.mean_diff:+.2f})", f"{r.method}, {r.image}, %{r.noise_pct} ({r.mean_diff:+.2f})")
        for _, r in sig_pos.iterrows()) or L("none", "yok")
    readme["results"] = ("**Extension, first iteration (E5, synthetic images): ACC (%) mean ± std over 10 seeds; Δ vs ASRFCM with the paper's coefficients, * = paired Wilcoxon p < 0.05.**\n\n"
                         + md_table(t5) + "\n\n**Guideline-format table (all synthetic settings):**\n\n" + md_table(gl))

    # ---------- FIS variants ----------
    fv = csv("e5_fis_variants_runs.csv")
    pv = fv.pivot_table(index="method", columns=["image", "noise_pct"], values="ACC")
    order = ["ASRFCM-paper", "full tri centroid", "full gauss centroid", "full tri bisector", "full tri mom", "full tri sugeno",
             "full unnormalised", "split tri centroid", "split gauss centroid", "split tri bisector", "split tri mom", "split tri sugeno"]
    pv = pv.loc[[o for o in order if o in pv.index]]
    pv.columns = [f"{i} {p}%" for i, p in pv.columns]
    tv = pv.reset_index().rename(columns={"method": L("Variant", "Varyant")})
    V["TABLE_fis_variants"] = html_table(tv.map(lambda v: f"{v:.2f}" if isinstance(v, float) else str(v)),
                                         L("Table VIII. FIS variants, ACC (%) mean of 10 seeds", "Tablo VIII. FIS varyantları, ACC (%), 10 tohumun ortalaması"))

    def rng(ref, fam):
        cols = pv.columns
        diffs = [abs(pv.loc[f, c] - pv.loc[ref, c]) for f in fam if f in pv.index for c in cols]
        return max(diffs)
    V["FV_full_maxdiff_nomom"] = f"{rng('full tri centroid', ['full gauss centroid', 'full tri bisector', 'full tri sugeno']):.2f}"
    V["FV_split_maxdiff_nomom"] = f"{rng('split tri centroid', ['split gauss centroid', 'split tri bisector', 'split tri sugeno']):.2f}"
    V["FV_full_mom_gain15"] = f"{max(pv.loc['full tri mom', c] - pv.loc['full tri centroid', c] for c in pv.columns if c.endswith('15%')):.2f}"
    V["FV_sugeno_maxdiff"] = f"{max(rng('full tri centroid', ['full tri sugeno']), rng('split tri centroid', ['split tri sugeno'])):.2f}"

    # ---------- E6 BSDS ----------
    b = csv("e6_bsds_runs.csv")
    b["image"] = b.image.str.replace("bsds:", "", regex=False)
    paper = csv("paper_reported_bsds.csv").astype({"image": str})
    pp = paper.pivot_table(index="image", columns="method", values="ACC")
    rgb_path = TABLES / "e6c_bsds_rgb_runs.csv"
    c = pd.read_csv(rgb_path) if rgb_path.exists() else None
    if c is not None:
        c["image"] = c.image.str.replace("bsdsrgb:", "", regex=False)
    rows = []
    M = ("FCM", "ASRFCM-paper", "FIS-full", "FIS-split")
    from src.data.bsds500 import PAPER_IDS
    for img in PAPER_IDS:
        g = b[b.image == img]
        r = [img, int(g.K.iloc[0])] + [f2s(g[g.method == m].ACC.mean()) for m in M]
        if c is not None:
            h = c[c.image == img]
            r += [f2s(h[h.method == m].ACC.mean()) for m in M]
        r += [f2s(pp.loc[img, "FCM"]), f2s(pp.loc[img, "Ours"])]
        rows.append(r)
    means = b.groupby("method").ACC.mean()
    last = [L("mean", "ortalama"), ""] + [f2s(means[m]) for m in M]
    if c is not None:
        cm = c.groupby("method").ACC.mean()
        last += [f2s(cm[m]) for m in M]
        V["E6c_fcm_mean"], V["E6c_asr_mean"] = f2s(cm["FCM"]), f2s(cm["ASRFCM-paper"])
        V["E6c_full_mean"], V["E6c_split_mean"] = f2s(cm["FIS-full"]), f2s(cm["FIS-split"])
        fc = c[c.method == "FCM"].groupby("image").ACC.mean()
        V["E6c_fcm_close"] = str(int(((fc - pp["FCM"]).abs() <= 2.0).sum()))
    last += [f2s(pp["FCM"].mean()), f2s(pp["Ours"].mean())]
    rows.append(last)
    cols = [L("Image", "Görüntü"), "K", "FCM", "ASRFCM", "+FIS full", "+FIS split"]
    if c is not None:
        cols += ["FCM (RGB)", "ASRFCM (RGB)", "+FIS full (RGB)", "+FIS split (RGB)"]
    cols += [L("FCM paper", "FCM makale"), L("ASRFCM paper", "ASRFCM makale")]
    tb = pd.DataFrame(rows, columns=cols)
    V["E6_fcm_mean"], V["E6_asr_mean"] = f2s(means["FCM"]), f2s(means["ASRFCM-paper"])
    V["E6_full_mean"], V["E6_split_mean"] = f2s(means["FIS-full"]), f2s(means["FIS-split"])
    V["E6_paper_fcm_mean"], V["E6_paper_ours_mean"] = f2s(pp["FCM"].mean()), f2s(pp["Ours"].mean())
    readme["results"] = readme.get("results", "") + (
        "\n\n**Real images (E6): BSDS500, 5 % mixed noise, ACC (%) mean of 10 seeds, gray and colour (RGB) protocols; paper values from its Table 9:**\n\n"
        + md_table(tb.astype(str))
        + "\n\nMore results: robustness per noise type `results/figures/e5_robustness_acc.png`, single-factor ablation `results/tables/e5_ablation_c2_summary.csv`, "
          "FIS variants `results/tables/e5_fis_variants_summary.csv`, sensitivity `results/figures/e4_sensitivity_acc.png`, run time `results/tables/e7_timing_summary.csv`, "
          "segmentations `results/figures/panel_synthetic.png`, `results/figures/panel_bsds.png`. Full discussion: [`report/report.pdf`](report/report.pdf).")
    V["TABLE_bsds"] = html_table(tb.astype(str), L("Table IX. BSDS500, 5 % mixed noise: ACC (%), mean of 10 seeds, on gray images and on colour images (RGB); paper-reported values from Table 9 of [1]",
                                                   "Tablo IX. BSDS500, %5 karışık gürültü: ACC (%), 10 tohumun ortalaması, gri ve renkli (RGB) görüntülerde; makale değerleri [1]'in Tablo 9'undan"),
                                 wide=True)
    V["E6_text"] = L(
        f"On the eight BSDS500 images (gray-level protocol, Table&nbsp;IX) the reproduced method raises the mean ACC of FCM from {V['E6_fcm_mean']} to "
        f"{V['E6_asr_mean']}&nbsp;% (paper-reported: {V['E6_paper_fcm_mean']} → {V['E6_paper_ours_mean']}&nbsp;%). Our FCM is lower than the paper's because "
        f"the paper clustered the color images (Section&nbsp;IX). <b>H2 is rejected:</b> the fuzzy-rule variants do not raise the mean ACC "
        f"(full {V['E6_full_mean']}&nbsp;%, split {V['E6_split_mean']}&nbsp;%).",
        f"Sekiz BSDS500 görüntüsünde (gri düzey protokolü, Tablo&nbsp;IX) yeniden gerçekleştirilen yöntem ortalama ACC'yi belirgin biçimde yükseltiyor: "
        f"FCM {V['E6_fcm_mean']} → yöntem {V['E6_asr_mean']}&nbsp;% (makalede: {V['E6_paper_fcm_mean']} → {V['E6_paper_ours_mean']}&nbsp;%). Bizim FCM değerimiz makaledekinden düşük, çünkü "
        f"makale renkli görüntüleri kümelemiş (Bölüm&nbsp;IX). <b>H2 reddedildi:</b> bulanık kural varyantları ortalama ACC'yi artırmıyor "
        f"(full {V['E6_full_mean']}&nbsp;%, split {V['E6_split_mean']}&nbsp;%).")
    if "E6c_asr_mean" in V:
        V["E6_text"] += L(
            f" For the colour re-run we use the minimal multichannel generalization of D-043 (ξ and ϑ per channel, Euclidean distances in RGB, "
            f"one α, β, γ per pixel from channel-averaged differences; noise added to each channel). On the colour images, our FCM matches the paper-reported FCM within two points on {V['E6c_fcm_close']} of 8 images "
            f"(mean {V['E6c_fcm_mean']} vs {V['E6_paper_fcm_mean']}&nbsp;%), and the reproduced method reaches {V['E6c_asr_mean']}&nbsp;% "
            f"(paper-reported {V['E6_paper_ours_mean']}&nbsp;%); the FIS variants give {V['E6c_full_mean']} (full) and {V['E6c_split_mean']}&nbsp;% (split).",
            f" Renkli tekrarda D-043'teki en küçük çok kanallı genellemeyi kullanıyoruz (ξ ve ϑ kanal başına, RGB'de Öklid uzaklığı, kanal ortalamalı "
            f"farklardan piksel başına tek α, β, γ; gürültü her kanala ayrı ekleniyor). Renkli görüntülerde FCM'miz makaledeki FCM ile 8 görüntüden {V['E6c_fcm_close']} tanesinde "
            f"iki puan içinde örtüşüyor (ortalama {V['E6c_fcm_mean']} ve {V['E6_paper_fcm_mean']}&nbsp;%); yeniden gerçekleştirilen yöntemin ortalaması {V['E6c_asr_mean']}&nbsp;% "
            f"(makalede {V['E6_paper_ours_mean']}&nbsp;%), FIS varyantlarınınki {V['E6c_full_mean']} (full) ve {V['E6c_split_mean']}&nbsp;% (split).")

    # ---------- E7 timing ----------
    tm = csv("e7_timing_summary.csv")
    order_m = {"FCM": 0, "ASRFCM-paper": 1, "FIS-full": 2, "FIS-split": 3, "FIS-sigma": 4, "FIS-sigma+A": 5}
    tt = tm.assign(_o=tm.method.map(order_m)).sort_values(["pixels", "_o"]).drop(columns="_o")
    tt = tt[~tt.image.str.contains("128")]   # the 128x128 run stays in results/tables/e7_timing_summary.csv
    tt["image"] = tt.image.str.replace(" (42049)", "", regex=False).str.replace("x", "×", regex=False)
    tt["method"] = tt.method.str.replace("ASRFCM-paper", "ASRFCM", regex=False).str.replace("sigma", "σ", regex=False)
    tt["preprocess_s"] = tt.preprocess_s.map(f2s)
    tt["cluster_s"] = tt.cluster_s.map(f2s)
    tt["total_s"] = tt.total_s.map(f2s)
    tt["iterations"] = tt.iterations.map(lambda v: f"{v:.0f}")
    tt = tt.rename(columns={"image": L("Image", "Görüntü"), "method": L("Method", "Yöntem"),
                            "preprocess_s": L("Pre-proc. (s)", "Ön işlem (s)"), "cluster_s": L("Clustering (s)", "Kümeleme (s)"),
                            "total_s": L("Total (s)", "Toplam (s)"), "iterations": L("Iter.", "İter.")}).drop(columns=["pixels"])
    V["TABLE_timing"] = html_table(tt, L("Table XII. Run time on one laptop CPU core (mean of 3 runs, 5 % mixed noise; a 128×128 run is in results/tables/e7_timing_summary.csv)",
                                         "Tablo XII. Tek dizüstü işlemci çekirdeğinde çalışma süresi (3 koşunun ortalaması, %5 karışık gürültü; 128×128 koşusu results/tables/e7_timing_summary.csv dosyasında)"))
    V["n_tests"] = str(count_tests())
    from report.report_values_extra import extra
    extra(V, readme, html_table)
    from report.report_values_e8 import second_iteration
    second_iteration(V, readme, html_table)
    V.pop("C1_table_values", None)
    return V, readme


def f2s(x) -> str:
    return f"{float(x):.2f}"
