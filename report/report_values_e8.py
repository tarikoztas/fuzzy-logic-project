"""Report values for the second iteration of the extension (E8, D-044/D-045), English or Turkish.

All numbers come from results/tables/e8_*.csv (tuning log, test runs, Wilcoxon tests, hypothesis
verdicts written by experiments/analyze_second_iteration.py).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from report.build_report import mean_std
from report.report_values import L, md_table

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"
PAPER, FIXED, FS, FSA = "ASRFCM-paper", "sigma=0.9 (fixed)", "FIS-sigma", "FIS-sigma+A"


def csv(name: str) -> pd.DataFrame:
    return pd.read_csv(TABLES / name)


def f2(x) -> str:
    return f"{float(x):.2f}"


def second_iteration(V: dict, readme: dict, html_table) -> None:
    # ---- tuning ----
    tl = csv("e8_tuning_log.csv")
    cand = tl[~tl.reference]
    V["E8_n_configs"] = str(len(cand))
    T = tl.set_index("configuration").ACC_mean
    pick = lambda prefix: round(float(T[[i for i in T.index if i.startswith(prefix)][0]]) + 1e-9, 2)
    V["E8_tune_paper"], V["E8_tune_fixed"] = f2(pick("ref: ASRFCM-paper")), f2(pick("ref: sigma=0.9"))
    V["E8_tune_split"], V["E8_tune_A"] = f2(pick("ref: FIS-split")), f2(pick("T1 "))
    V["E8_tune_B"], V["E8_tune_AB"] = f2(pick("T2 ")), f2(pick("T3 "))
    V["E8_tune_C"] = f"{min(pick('T4 '), pick('T5 '), pick('T6 ')):.2f}–{max(pick('T4 '), pick('T5 '), pick('T6 ')):.2f}"
    V["E8_tune_T7"], V["E8_tune_T8"], V["E8_tune_T9"] = f2(pick("T7 ")), f2(pick("T8 ")), f2(pick("T9 "))

    # ---- main test grid ----
    d = csv("e8_second_iteration_runs.csv")
    w = csv("e8_second_iteration_wilcoxon.csv")
    acc = d.groupby(["image", "noise_pct", "method"]).ACC.mean().unstack("method")
    sig = d.groupby(["noise_pct", "method"]).sigma_used.mean().unstack("method")
    pooled = csv("e8_pooled_wilcoxon.csv")
    pz = lambda lvl, m, b: pooled[(pooled.noise_pct == lvl) & (pooled.method == m) & (pooled.baseline == b)].iloc[0]
    rows = []
    for img in ("sy1", "sy2", "sy3"):
        for p in (1, 5, 10, 15):
            g = d[(d.image == img) & (d.noise_pct == p)]
            r = [img, p, mean_std(g[g.method == PAPER].ACC), mean_std(g[g.method == FIXED].ACC)]
            for m in (FS, FSA):
                ww = w[(w.image == img) & (w.noise_pct == p) & (w.method == m)].iloc[0]
                r.append(f"{g[g.method == m].ACC.mean():.2f} ({ww.mean_diff:+.2f}{'*' if ww['significant_0.05'] else ''})")
            rows.append(r)
    t = pd.DataFrame(rows, columns=[L("Image", "Görüntü"), L("Noise %", "Gürültü %"), L("ASRFCM (σ = 0.3)", "ASRFCM (σ = 0.3)"),
                                    L("σ = 0.9 fixed", "σ = 0.9 sabit"), L("FIS-σ (Δ)", "FIS-σ (Δ)"), L("FIS-σ+A (Δ)", "FIS-σ+A (Δ)")])
    V["TABLE_e8"] = html_table(t, L("Table X. Second iteration on the test grid (seeds 0–9): ACC (%), mean ± std or mean; Δ = difference to ASRFCM with the paper's settings; * paired Wilcoxon p < 0.05",
                                    "Tablo X. Test ızgarasında ikinci iterasyon (tohum 0–9): ACC (%), ortalama ± std ya da ortalama; Δ = makale ayarlı ASRFCM'ye göre fark; * eşleştirilmiş Wilcoxon p < 0.05"),
                               wide=True)
    for lvl in (1, 5, 10, 15):
        V[f"E8_fs_gain{lvl}"] = f"{pz(lvl, FS, PAPER).mean_diff:+.2f}"
        V[f"E8_fsa_gain{lvl}"] = f"{pz(lvl, FSA, PAPER).mean_diff:+.2f}"
        V[f"E8_fs_vs_fixed{lvl}"] = f"{pz(lvl, FS, FIXED).mean_diff:+.2f}"
        V[f"E8_sigma{lvl}"] = f"{sig.loc[lvl, FS]:.2f}"
    V["E8_fs_p15"] = f"{pz(15, FS, PAPER).p_value:.0e}".replace("e-0", "e-")
    big = acc.loc[[("sy2", 15), ("sy3", 15)]]
    V["E8_fs_15_sy2"], V["E8_fs_15_sy3"] = f2(big.loc[("sy2", 15), FS]), f2(big.loc[("sy3", 15), FS])
    V["E8_paper_15_sy2"], V["E8_paper_15_sy3"] = f2(big.loc[("sy2", 15), PAPER]), f2(big.loc[("sy3", 15), PAPER])
    e2 = csv("e2_asrfcm_vs_paper.csv")
    pr = e2[e2.metric == "ACC"].set_index(["image", "noise_pct"]).paper_reported
    V["E8_reported_15_sy2"], V["E8_reported_15_sy3"] = f2(pr[("sy2", 15)]), f2(pr[("sy3", 15)])
    low = (acc[FS] - acc[PAPER]).loc[(slice(None), [1, 5])]
    V["E8_fs_worst_low"] = f"{low.min():+.2f}"
    dc = acc[FS] - acc[FIXED]
    V["E8_fs_fixed_range"] = f"{dc.min():+.2f} … {dc.max():+.2f}"
    d6 = acc[FSA] - acc[PAPER]
    V["E8_fsa_worst"] = f"{d6.min():+.2f}"
    ful = d.groupby("method").ACC.mean()
    V["E8_mean_paper"], V["E8_mean_fs"], V["E8_mean_fsa"], V["E8_mean_full"] = (f2(ful[m]) for m in (PAPER, FS, FSA, "FIS-full"))
    V["E8_mean_fixed"] = f2(ful[FIXED])
    sp = acc.loc[("sy2", 1)]
    V["E8_fsa_sy2_1"], V["E8_fs_sy2_1"] = f2(sp[FSA]), f2(sp[FS])
    hyp = csv("e8_hypotheses.csv")
    ov = hyp[hyp.criterion == "overall"].set_index("hypothesis").holds
    V["E8_H5"] = L("holds", "tuttu") if ov["H5"] else L("is rejected", "reddedildi")
    V["E8_H6"] = L("holds", "tuttu") if ov["H6"] else L("is rejected", "reddedildi")
    ctl = bool(hyp[hyp.hypothesis == "H5-control"].holds.iloc[0])
    V["E8_H5c"] = L("holds", "tuttu") if ctl else L("does not hold", "tutmadı")

    gl = pd.read_csv(TABLES / "e8_baseline_vs_improved.csv", dtype=str)
    gl["Metric"] = gl["Metric"].replace({"Kappa": "Kappa (Cohen)", "Kappa_paper": L("Kappa (paper's definition)", "Kappa (makalenin tanımı)"),
                                         "VPC": "V_PC", "VPE": "V_PE", "Iterations": L("Iterations", "İterasyon"),
                                         "Time per 256x256 image (s, E7)": L("Time per 256x256 image (s, E7)", "256×256 görüntü başına süre (s, E7)")})
    gl.columns = [c.replace("sigma", "σ") for c in gl.columns]
    if L("en", "tr") == "tr":
        gl.columns = [c.replace("Metric", "Ölçüt").replace("Baseline", "Temel").replace("Improved", "Geliştirilen")
                      .replace("Change", "Değişim") for c in gl.columns]
    V["TABLE_e8_guideline"] = html_table(gl, L("Table XI. Second iteration, baseline vs improved over all synthetic test settings (12 settings × 10 seeds; guideline format)",
                                               "Tablo XI. İkinci iterasyon, tüm sentetik test ayarlarında temel ve geliştirilen yöntem (12 ayar × 10 tohum; yönerge biçimi)"),
                                         wide=True)

    # ---- BSDS500 gray / colour ----
    for tag, name in (("gray", "e8_bsds_second"), ("rgb", "e8_bsds_rgb_second")):
        p = TABLES / f"{name}_runs.csv"
        if not p.exists():
            continue
        b = pd.read_csv(p)
        mm = b.groupby("method").ACC.mean()
        for key, m in (("paper", PAPER), ("fixed", FIXED), ("fs", FS), ("fsa", FSA), ("fcm", "FCM")):
            V[f"E8_bsds_{tag}_{key}"] = f2(mm[m])
        V[f"E8_bsds_{tag}_sigma"] = f"{b[b.method == FS].sigma_used.mean():.2f}"
        wb = csv(f"{name}_wilcoxon.csv")
        V[f"E8_bsds_{tag}_fs_sig"] = str(int(((wb.method == FS) & (wb.mean_diff > 0) & wb["significant_0.05"]).sum()))
        V[f"E8_bsds_{tag}_fs_loss"] = str(int(((wb.method == FS) & (wb.mean_diff < 0) & wb["significant_0.05"]).sum()))
        V[f"E8_bsds_{tag}_fsa_sig"] = str(int(((wb.method == FSA) & (wb.mean_diff > 0) & wb["significant_0.05"]).sum()))
        V[f"E8_bsds_{tag}_fsa_loss"] = str(int(((wb.method == FSA) & (wb.mean_diff < 0) & wb["significant_0.05"]).sum()))

    # ---- robustness ----
    p = TABLES / "e8_robustness_second_runs.csv"
    if p.exists():
        r = pd.read_csv(p).groupby(["noise_kind", "noise_pct", "method"]).ACC.mean().unstack("method")
        kname = {"gaussian": L("Gaussian", "Gauss"), "speckle": L("speckle", "benek"),
                 "salt_pepper": L("salt-and-pepper", "tuz-biber"), "mixed": L("mixed", "karışık")}
        for kind in ("gaussian", "speckle", "salt_pepper", "mixed"):
            for lvl in (0, 1, 20):
                for key, m in (("paper", PAPER), ("fixed", FIXED), ("fs", FS), ("fsa", FSA)):
                    V[f"E8_rob_{kind}_{lvl}_{key}"] = f"{r.loc[(kind, lvl), m]:.2f}"
        diff = (r[FS] - r[FIXED])
        V["E8_rob_fs_fixed_min"], V["E8_rob_fs_fixed_max"] = f"{diff.min():+.2f}", f"{diff.max():+.2f}"
        worst = diff.idxmin()
        V["E8_rob_fs_fixed_worst"] = f"{kname[worst[0]]} {worst[1]}&nbsp;%"
        d2 = (r[FS] - r[PAPER])
        V["E8_rob_fs_paper_min"], V["E8_rob_fs_paper_max"] = f"{d2.min():+.2f}", f"{d2.max():+.2f}"
        V["E8_rob_fs_paper_minabs"] = f"{max(0.0, -d2.min()):.2f}"
        w2, b2 = d2.idxmin(), d2.idxmax()
        V["E8_rob_fs_paper_worst"] = f"{kname[w2[0]]} {w2[1]}&nbsp;%"
        V["E8_rob_fs_paper_best"] = f"{kname[b2[0]]} {b2[1]}&nbsp;%"
        V["E8_rob_fs_never_below"] = bool(d2.min() > -0.05)
        d3 = (r[FSA] - r[PAPER])
        V["E8_rob_fsa_paper_min"], V["E8_rob_fsa_paper_max"] = f"{d3.min():+.2f}", f"{d3.max():+.2f}"
        w3 = d3.idxmin()
        V["E8_rob_fsa_paper_worst"] = f"{kname[w3[0]]} {w3[1]}&nbsp;%"

    # ---- text: beyond the test grid (BSDS500 + noise types) ----
    if "E8_bsds_rgb_fs" in V and "E8_rob_fs_fixed_min" in V:
        g = lambda k: V[k]
        V["E8_beyond_text"] = L(
            f"On the eight BSDS500 images FIS-σ raises the mean ACC from {g('E8_bsds_gray_paper')} to {g('E8_bsds_gray_fs')}&nbsp;% on gray images "
            f"(fixed σ = 0.9: {g('E8_bsds_gray_fixed')}&nbsp;%) and from {g('E8_bsds_rgb_paper')} to {g('E8_bsds_rgb_fs')}&nbsp;% on colour images "
            f"(fixed σ = 0.9: {g('E8_bsds_rgb_fixed')}&nbsp;%); FIS-σ+A gives {g('E8_bsds_gray_fsa')} and {g('E8_bsds_rgb_fsa')}&nbsp;%. On colour images the rule "
            f"selects only σ ≈ {g('E8_bsds_rgb_sigma')} (gray: {g('E8_bsds_gray_sigma')}), because the estimate is computed on the channel mean, in which the "
            f"independent noise of the three channels partly cancels. Over the four noise types at 0–20&nbsp;% (repository figure "
            f"<code>e8_robustness_acc.png</code>) FIS-σ is "
            + (f"never more than 0.05 point below the paper's settings" if V["E8_rob_fs_never_below"] else
               f"at most {g('E8_rob_fs_paper_minabs')} points below the paper's settings ({g('E8_rob_fs_paper_worst')})")
            + f" and up to {g('E8_rob_fs_paper_max')} points better ({g('E8_rob_fs_paper_best')}); compared with a fixed σ = 0.9 it differs by "
            f"{g('E8_rob_fs_fixed_min')} to {g('E8_rob_fs_fixed_max')} points, the largest loss being at {g('E8_rob_fs_fixed_worst')}, where the "
            f"median-based estimate does not detect the sparse impulses (Section&nbsp;IX). FIS-σ+A differs from the paper's settings by "
            f"{g('E8_rob_fsa_paper_min')} to {g('E8_rob_fsa_paper_max')} points (largest loss: {g('E8_rob_fsa_paper_worst')}).",
            f"Sekiz BSDS500 görüntüsünde FIS-σ ortalama ACC'yi gri görüntülerde {g('E8_bsds_gray_paper')} → {g('E8_bsds_gray_fs')}&nbsp;% "
            f"(sabit σ = 0.9: {g('E8_bsds_gray_fixed')}&nbsp;%), renkli görüntülerde {g('E8_bsds_rgb_paper')} → {g('E8_bsds_rgb_fs')}&nbsp;% yükseltiyor "
            f"(sabit σ = 0.9: {g('E8_bsds_rgb_fixed')}&nbsp;%); FIS-σ+A sırasıyla {g('E8_bsds_gray_fsa')} ve {g('E8_bsds_rgb_fsa')}&nbsp;% veriyor. Renkli görüntülerde "
            f"kural yalnızca σ ≈ {g('E8_bsds_rgb_sigma')} seçiyor (gri: {g('E8_bsds_gray_sigma')}), çünkü tahmin kanal ortalaması üzerinde hesaplanıyor ve üç kanalın "
            f"bağımsız gürültüsü bu ortalamada kısmen sönüyor. %0–20 aralığındaki dört gürültü türünde (depodaki <code>e8_robustness_acc_tr.png</code> şekli) FIS-σ "
            + ("hiçbir ayarda makale ayarlarının 0.05 puandan fazla altında değil" if V["E8_rob_fs_never_below"] else
               f"makale ayarlarının en fazla {g('E8_rob_fs_paper_minabs')} puan altında ({g('E8_rob_fs_paper_worst')})")
            + f" ve en çok {g('E8_rob_fs_paper_max')} puan daha iyi ({g('E8_rob_fs_paper_best')}); sabit σ = 0.9 ile farkı {g('E8_rob_fs_fixed_min')} ile "
            f"{g('E8_rob_fs_fixed_max')} puan arasında, en büyük kayıp {g('E8_rob_fs_fixed_worst')} ayarında: medyana dayalı tahmin seyrek dürtüleri görmüyor "
            f"(Bölüm&nbsp;IX). FIS-σ+A ile makale ayarları arasındaki fark {g('E8_rob_fsa_paper_min')} ile {g('E8_rob_fsa_paper_max')} puan "
            f"(en büyük kayıp: {g('E8_rob_fsa_paper_worst')}).")
        V["E8_rule_value"] = L(
            f"noise-free images: FIS-σ {g('E8_rob_mixed_0_fs')}&nbsp;%, fixed σ = 0.9 {g('E8_rob_mixed_0_fixed')}&nbsp;%, paper {g('E8_rob_mixed_0_paper')}&nbsp;%",
            f"gürültüsüz görüntüler: FIS-σ {g('E8_rob_mixed_0_fs')}&nbsp;%, sabit σ = 0.9 {g('E8_rob_mixed_0_fixed')}&nbsp;%, makale {g('E8_rob_mixed_0_paper')}&nbsp;%")
        sp_fs, sp_fx = g("E8_rob_salt_pepper_20_fs"), g("E8_rob_salt_pepper_20_fixed")
        V["E8_sp20"] = L(f"{sp_fs} vs {sp_fx}&nbsp;% at 20&nbsp;%", f"%20'de {sp_fs} ve {sp_fx}&nbsp;%")
    else:  # results not available yet
        V["E8_beyond_text"] = V["E8_rule_value"] = V["E8_sp20"] = "–"

    readme["second_iteration"] = (
        "**Second iteration (E8, pre-registered in `report/checkpoints/CP6_second_iteration_plan.md`): ACC (%) on the synthetic test grid, "
        "mean ± std over seeds 0–9; Δ vs ASRFCM with the paper's settings, * = paired Wilcoxon p < 0.05.**\n\n" + md_table(t)
        + f"\n\nH5 (FIS-σ better than the paper at 10/15 % without loss at 1/5 %) {V['E8_H5']}; H6 (FIS-σ+A never below the paper) {V['E8_H6']}; "
          f"as expected, FIS-σ is practically equal to a fixed σ = 0.9 on this grid (differences {V['E8_fs_fixed_range']} points). "
          "Tuning log: `results/tables/e8_tuning_log.csv`; hypotheses: `results/tables/e8_hypotheses.csv`; figures `results/figures/e8_*.png`.\n\n"
          "**Guideline-format table (second iteration):**\n\n" + md_table(gl))
