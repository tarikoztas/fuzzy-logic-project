"""Second part of the report values: references, decisions/rule tables, and the text
blocks for E4, C1, C2, E6, E7 — all computed from results/tables/*.csv."""
from __future__ import annotations

import platform
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"

REF_MAP = {34: 29, 35: 30, 36: 31}   # report numbering ([29]-[33] of references/README.md are not cited)
CITED = list(range(1, 29)) + [34, 35, 36]


def csv(name: str) -> pd.DataFrame:
    return pd.read_csv(TABLES / name)


def references_html() -> str:
    text = (ROOT / "references" / "README.md").read_text(encoding="utf-8")
    entries = {}
    for line in text.splitlines():
        m = re.match(r"^\[(\d+)\] \[V[^\]]*\] (.*)$", line)
        if m:
            entries[int(m.group(1))] = m.group(2)
        m = re.match(r"^\| \[(\d+)\] \| V[^|]*\| (.*?) \|", line)
        if m:
            entries[int(m.group(1))] = m.group(2)
    items = []
    for n in CITED:
        e = entries[n]
        e = re.sub(r"\s*\*\*\(.*?\)\*\*\s*$", "", e)   # trailing **(name)**
        e = re.sub(r"\s*\*\(.*?\)\*\s*$", "", e)       # trailing *(note)*
        e = re.sub(r"\*(.+?)\*", r"<i>\1</i>", e)
        items.append(f'<li value="{REF_MAP.get(n, n)}">{e.strip()}</li>')
    return '<ol class="refs">' + "".join(items) + "</ol>"


def renumber_citations(html: str) -> str:
    """[34] -> [29] etc. in the body text (references list already uses report numbers)."""
    for old, new in REF_MAP.items():
        html = html.replace(f"[{old}]", f"[{new}]")
    return html


def extra(V: dict, readme: dict, html_table) -> None:
    V["cpu_note"] = f"{platform.system()} {platform.release()}, {platform.machine()} CPU, one core, Python {platform.python_version()}"

    rows = [
        ["Synthetic images", "sy1–sy3 extracted from Fig. 9 of [1], 256×256"],
        ["BSDS500 ground truth", "2–4 class maps of Fig. 22 of [1], extracted; K = 2,3,3,3,4,2,2,2"],
        ["Mixed noise p %", "Gaussian (var. p) → speckle (var. p) → salt-and-pepper (density p)"],
        ["Reward-set size", "⌊0.618(N<sub>R</sub>−1)⌋ as in Fig. 1 of [1] (text: ⌈·⌉, ablation)"],
        ["Eq. 10", "y<sub>q</sub> instead of the printed y<sub>j</sub>"],
        ["NLM intensities", "[0,1] (Alg. 3 step 1), h² = g·w², normalized patch kernel"],
        ["Complex sub-bands", "weights from magnitudes, applied to real and imaginary parts"],
        ["Eqs. 15–16", "signed exp(y−ξ) as printed; |y−ξ| in the ablation"],
        ["Empty column after threshold", "keep η of that pixel (reproduces the reported V<sub>PC</sub>)"],
        ["Label matching", "Hungarian; F-score macro-averaged; Cohen's kappa"],
    ]
    V["TABLE_decisions"] = html_table(pd.DataFrame(rows, columns=["Ambiguity", "Our choice"]),
                                      "Table I. Main interpretation choices (details and evidence: report/decisions.md)")
    rb = csv("fis_rule_base.csv")
    rb.columns = ["Rule", "Dev", "Dis", "α", "β", "γ"]
    V["TABLE_rules"] = html_table(rb, "Table II. Rule base (IF Dev AND Dis THEN α, β, γ)")

    # ---- C2 single-factor ablation ----
    c2 = csv("e5_ablation_c2_runs.csv")
    pv = c2.pivot_table(index="method", columns=["image", "noise_pct"], values="ACC")
    it = c2.pivot_table(index="method", columns="noise_pct", values="Iterations")
    order = ["paper", "ratio=0.5", "ratio=0.7", "ratio=0.8", "rounding=ceil", "sigma=0.6", "sigma=0.9", "dG=abs",
             "empty=argmax", "nlm_scale=255"]
    names = {"paper": "paper settings", "ratio=0.5": "ρ = 0.5", "ratio=0.7": "ρ = 0.7", "ratio=0.8": "ρ = 0.8",
             "rounding=ceil": "⌈·⌉ reward size", "sigma=0.6": "σ = 0.6", "sigma=0.9": "σ = 0.9",
             "dG=abs": "|y−ξ| in Eqs. 15–16", "empty=argmax": "empty column: argmax", "nlm_scale=255": "NLM on 0–255"}
    tab = pv.loc[order].map(lambda v: f"{v:.2f}")
    tab.columns = [f"{i} {p}%" for i, p in tab.columns]
    tab["Iter. 15%"] = it.loc[order, 15].map(lambda v: f"{v:.1f}")
    tab = tab.reset_index().rename(columns={"method": "Variant"})
    tab["Variant"] = tab["Variant"].map(names)
    V["TABLE_c2"] = html_table(tab.astype(str), "Table V. Single-factor ablation, ACC (%) mean of 10 seeds, mixed noise", wide=True)
    e2 = csv("e2_asrfcm_vs_paper.csv")
    pa = e2[e2.metric == "ACC"].set_index(["image", "noise_pct"]).paper_reported
    gb = [pa[(i, 15)] - pv.loc["paper", (i, 15)] for i in ("sy2", "sy3")]
    ga = [pa[(i, 15)] - pv.loc["sigma=0.9", (i, 15)] for i in ("sy2", "sy3")]
    P = lambda m, i, p: f"{pv.loc[m, (i, p)]:.2f}"
    V["C2_text"] = (
        f"Table V changes one choice at a time. The reward factor has the largest effect: with σ = 0.9 the ACC at 15&nbsp;% noise rises from "
        f"{P('paper', 'sy2', 15)} to {P('sigma=0.9', 'sy2', 15)}&nbsp;% on sy2 and from {P('paper', 'sy3', 15)} to {P('sigma=0.9', 'sy3', 15)}&nbsp;% on sy3; "
        f"the gap to the paper-reported values shrinks from {gb[0]:.1f}/{gb[1]:.1f} to {ga[0]:.1f}/{ga[1]:.1f} points and the iterations at 15&nbsp;% fall from "
        f"{it.loc['paper', 15]:.1f} to {it.loc['sigma=0.9', 15]:.1f}. The golden ratio is not special: ρ = 0.5 gives the same or slightly higher ACC, whereas 0.7 "
        f"and 0.8 are worse at high noise, and the rounding of the reward-set size hardly matters. The absolute difference in Eqs. 15–16 is better than the printed "
        f"signed one at 15&nbsp;% (sy3: {P('dG=abs', 'sy3', 15)} vs {P('paper', 'sy3', 15)}&nbsp;%). Making empty columns crisp (argmax) forces V<sub>PC</sub> = 100&nbsp;% "
        f"and costs ACC on sy2 at 5&nbsp;% ({P('empty=argmax', 'sy2', 5)} vs {P('paper', 'sy2', 5)}&nbsp;%), and running the non-local means on 0–255 intensities is "
        f"clearly worse at 15&nbsp;% (sy3: {P('nlm_scale=255', 'sy3', 15)}&nbsp;%).")
    V["C2_sigma_gap"] = f"{gb[0]:.1f}/{gb[1]:.1f} to {ga[0]:.1f}/{ga[1]:.1f}"

    # ---- E4 sensitivity ----
    se = csv("e4_sensitivity_summary.csv")
    sig = se[se.param == "sigma"].pivot_table(index="value", columns="image", values="ACC_mean")
    dl = se[se.param == "delta"].pivot_table(index="value", columns="image", values="Iterations_mean")
    ww = se[se.param == "w"].pivot_table(index="value", columns="image", values="ACC_mean")
    kk = se[se.param == "k"].pivot_table(index="value", columns="image", values="ACC_mean")
    dacc = se[se.param == "delta"].pivot_table(index="value", columns="image", values="ACC_mean")
    kk5 = kk.loc[kk.index >= 5]
    best_delta = dl["sy3"].idxmin()
    V["E4_text"] = (
        f"At 5&nbsp;% noise the method is insensitive to σ, w and δ (Fig.&nbsp;4): over σ ∈ [0.05, 0.9], w ∈ {{3, 5, 7, 9}} and δ ∈ [0, 0.8] the ACC of each image "
        f"varies by at most {(sig.max() - sig.min()).max():.2f}, {(ww.max() - ww.min()).max():.2f} and {(dacc.max() - dacc.min()).max():.2f} points. "
        f"Unlike Fig.&nbsp;10 of [1], the ACC does not decrease above σ = 0.4; on sy3 it increases slightly up to σ = 0.9 "
        f"({sig.loc[0.3, 'sy3']:.2f} → {sig.loc[0.9, 'sy3']:.2f}&nbsp;%), consistent with Section&nbsp;VIII-E. For k ≥ 5 the ACC is stable "
        f"(range {(kk5.max() - kk5.min()).max():.2f} points), while k = 1 degrades it (sy3: {kk.loc[1.0, 'sy3']:.2f}&nbsp;%), in line with the paper's statement that "
        f"k should exceed 5. The sparsity factor mainly controls convergence: on sy3 the iterations fall from {dl.loc[0.0, 'sy3']:.1f} without sparsity (δ = 0) to a "
        f"minimum of {dl['sy3'].min():.1f} at δ = {best_delta:g} and rise again for larger δ ({dl.loc[0.4, 'sy3']:.1f} at the paper's δ = 0.4).")

    # ---- C1 robustness ----
    rob = csv("e5_robustness_runs.csv")
    r = rob.groupby(["noise_kind", "noise_pct", "method"]).ACC.mean().unstack("method")
    at = lambda kind, p, m: f"{r.loc[(kind, p), m]:.1f}"
    V["C1_text"] = (
        f"Fig.&nbsp;6 separates the components of the mixed noise (values: mean over sy1–sy3, FCM → reproduced method at 20&nbsp;%). "
        f"Salt-and-pepper ({at('salt_pepper', 20, 'FCM')} → {at('salt_pepper', 20, 'ASRFCM-paper')}&nbsp;%) and speckle noise "
        f"({at('speckle', 20, 'FCM')} → {at('speckle', 20, 'ASRFCM-paper')}&nbsp;%) are almost completely removed: impulses sit at the ends of the sorted "
        f"neighbourhood and fall into the penalty set, and speckle leaves dark regions untouched. Gaussian noise is harder "
        f"({at('gaussian', 20, 'FCM')} → {at('gaussian', 20, 'ASRFCM-paper')}&nbsp;%), and the combination is clearly the hardest case "
        f"({at('mixed', 20, 'FCM')} → {at('mixed', 20, 'ASRFCM-paper')}&nbsp;%): the method copes well with each component alone but not with their sum at the "
        f"same parameter. On noise-free images the method is slightly below FCM ({at('mixed', 0, 'ASRFCM-paper')} vs {at('mixed', 0, 'FCM')}&nbsp;%) because the "
        f"spatial terms smooth thin structures; the pre-registered FIS, which trusts consistent pixels, keeps {at('mixed', 0, 'FIS-full')}&nbsp;% there and is "
        f"also better at 1&nbsp;% noise (e.g. Gaussian: {at('gaussian', 1, 'FIS-full')} vs {at('gaussian', 1, 'ASRFCM-paper')}&nbsp;%). This is the regime the rule "
        f"base was designed for; with more noise its trust in the pixel becomes a liability (Gaussian 20&nbsp;%: {at('gaussian', 20, 'FIS-full')}&nbsp;%). The split "
        f"variant is equal to or slightly better than the paper's coefficients for impulse and speckle noise up to 10&nbsp;% "
        f"(salt-and-pepper 10&nbsp;%: {at('salt_pepper', 10, 'FIS-split')} vs {at('salt_pepper', 10, 'ASRFCM-paper')}&nbsp;%) and falls behind for Gaussian and mixed "
        f"noise at high density.")
    V["C1_table_values"] = r

    # ---- E7 timing ----
    tm = csv("e7_timing_summary.csv")
    t256 = tm[tm.image.str.contains("256")].set_index("method")
    V["E7_text"] = (
        f"On a 256×256 image FCM takes {t256.loc['FCM', 'total_s']:.2f}&nbsp;s and the reproduced method {t256.loc['ASRFCM-paper', 'total_s']:.2f}&nbsp;s, "
        f"of which {t256.loc['ASRFCM-paper', 'preprocess_s']:.2f}&nbsp;s are spent on ξ and ϑ (Table&nbsp;XI); the sparse clustering itself is fast because it "
        f"converges in few iterations. The Mamdani FIS adds {t256.loc['FIS-full', 'preprocess_s'] - t256.loc['ASRFCM-paper', 'preprocess_s']:.2f}&nbsp;s "
        f"(nine rules evaluated on a 201-point output grid for every pixel); the zero-order Sugeno variant avoids this grid.")

    V["REFERENCES"] = references_html()
    V["GENAI_TEXT"] = (
        "Claude Code (Anthropic) was used as an assistant throughout the project: for planning and literature-search support (every reference was then checked "
        "against Crossref, and only abstracts that could be read are used for claims about a method), for writing and debugging the Python implementation and the "
        "experiment, analysis and plotting scripts, for checking the paper's equations and tables, and for language editing of the report and the slides. The tool "
        "did not produce any result by itself: all numbers come from running the code in the repository, every table and figure is generated from the result files, "
        "and all decisions and deviations are logged with their evidence (report/decisions.md). The student reviewed the code, the decisions and the text and is "
        "responsible for the content.")
