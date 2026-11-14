"""Figures of the fuzzy inference system (D-033): membership functions, control
surfaces, and the inference steps for one pixel."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from src.fcm.fis_coefficients import build_fis, input_terms, output_terms  # noqa: E402
from src.fuzzy.defuzz import METHODS  # noqa: E402

from .plots import GRID, INK, MUTED, SERIES  # noqa: E402


def _style(ax):
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=8)


TR_TERMS = {"Small": "Küçük", "Medium": "Orta", "Large": "Büyük", "Low": "Düşük", "High": "Yüksek"}


def _term(name: str, lang: str) -> str:
    return TR_TERMS.get(name, name) if lang == "tr" else name


def _save(fig, stem):
    for ext in ("png", "pdf"):
        fig.savefig(f"{stem}.{ext}", dpi=200)
    plt.close(fig)


def membership_functions(stem: str, lang: str = "en") -> None:
    tr = lang == "tr"
    x = np.linspace(0, 1, 501)
    fig, axes = plt.subplots(2, 2, figsize=(9, 5.2), sharex=True)
    titles = (("Girdiler Dev, Dis (gri fark)" if tr else "Inputs Dev, Dis (gray difference)", input_terms),
              ("Çıktılar α, β, γ (güven)" if tr else "Outputs alpha, beta, gamma (trust)", output_terms))
    for row, shape in enumerate(("tri", "gauss")):
        for col, (title, terms_of) in enumerate(titles):
            ax = axes[row][col]
            for i, (name, mf) in enumerate(terms_of(shape).items()):
                ax.plot(x, mf(x), color=SERIES[i], linewidth=2, label=_term(name, lang))
            kind = ("üçgen" if shape == "tri" else "Gauss") if tr else ("triangular" if shape == "tri" else "Gaussian")
            ax.set_title(f"{title} - {kind}", fontsize=9, color=INK)
            ax.set_ylim(-0.03, 1.05)
            ax.set_ylabel("üyelik derecesi" if tr else "membership", fontsize=8, color=INK)
            ax.legend(frameon=False, fontsize=8)
            _style(ax)
    for ax in axes[1]:
        ax.set_xlabel("değer" if tr else "value", fontsize=8, color=INK)
    fig.tight_layout()
    _save(fig, stem)


def control_surfaces(stem: str, shape: str = "tri", defuzz: str = "centroid") -> None:
    fis = build_fis(shape, defuzz)
    g = np.linspace(0, 0.6, 121)
    dev, dis = np.meshgrid(g, g, indexing="xy")
    out = fis.evaluate(Dev=dev.ravel(), Dis=dis.ravel())
    s = out["alpha"] + out["beta"] + out["gamma"]
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4))
    for ax, name in zip(axes, ("alpha", "beta", "gamma")):
        z = (out[name] / s).reshape(dev.shape)
        im = ax.imshow(z, origin="lower", extent=(0, 0.6, 0, 0.6), cmap="Blues", vmin=0, vmax=0.6, aspect="auto")
        ax.set_title(f"normalised {name}", fontsize=9, color=INK)
        ax.set_xlabel("Dev = |y - (xi+theta)/2|", fontsize=8, color=INK)
        ax.set_ylabel("Dis = |xi - theta|", fontsize=8, color=INK)
        ax.tick_params(colors=MUTED, labelsize=8)
        fig.colorbar(im, ax=ax, fraction=0.046)
    fig.tight_layout()
    _save(fig, stem)


def inference_example(stem: str, dev: float, dis: float, output: str = "gamma", lang: str = "en") -> dict:
    """Fuzzification -> rule firing -> clipped consequents -> aggregation -> crisp value, for one pixel."""
    fis = build_fis()
    w = fis.firing_strengths({"Dev": np.array([dev]), "Dis": np.array([dis])})[:, 0]
    out_var = next(o for o in fis.outputs if o.name == output)
    z, agg = fis.aggregate(w[:, None], out_var)
    crisp = {m: float(f(z, agg)[0]) for m, f in METHODS.items()}
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.3), gridspec_kw={"width_ratios": [1, 1.2, 1.3]})
    x = np.linspace(0, 1, 501)
    for i, (name, mf) in enumerate(input_terms("tri").items()):
        axes[0].plot(x, mf(x), color=SERIES[i], linewidth=2, label=_term(name, lang))
    tr = lang == "tr"
    axes[0].axvline(dev, color=INK, linestyle="--", linewidth=1)
    axes[0].axvline(dis, color=MUTED, linestyle=":", linewidth=1.5)
    axes[0].set_xlim(0, 0.6)
    axes[0].set_title(f"1. bulanıklaştırma (Dev={dev}, kesikli; Dis={dis}, noktalı)" if tr else
                      f"1. fuzzification (Dev={dev}, dashed; Dis={dis}, dotted)", fontsize=9, color=INK)
    axes[0].legend(frameon=False, fontsize=8)
    labels = [f"R{i + 1}" for i in range(len(fis.rules))]
    axes[1].bar(labels, w, color=SERIES[0], width=0.6)
    axes[1].set_ylim(0, 1)
    axes[1].set_title("2. kural ateşlenme derecesi (VE = min)" if tr else "2. rule firing strength (AND = min)", fontsize=9, color=INK)
    axes[2].fill_between(z, agg[0], color=SERIES[0], alpha=0.35,
                         label="birleşik küme (kırpılmışların max'ı)" if tr else "aggregated set (max of clipped)")
    names = {"centroid": "ağırlık merkezi", "bisector": "açıortay", "mom": "MOM"} if tr else {}
    for m, ls in zip(crisp, ("-", "--", ":")):
        axes[2].axvline(crisp[m], color=INK, linestyle=ls, linewidth=1.2, label=f"{names.get(m, m)} = {crisp[m]:.3f}")
    axes[2].set_ylim(0, 1.05)
    sym = {"alpha": "α", "beta": "β", "gamma": "γ"}.get(output, output) if tr else output
    axes[2].set_title(f"3-4. {sym}: çıkarım, birleştirme, durulaştırma" if tr else
                      f"3-4. {output}: implication, aggregation, defuzzification", fontsize=9, color=INK)
    axes[2].legend(frameon=False, fontsize=7)
    for ax in axes:
        _style(ax)
    fig.tight_layout()
    _save(fig, stem)
    return {"firing": dict(zip(labels, np.round(w, 3).tolist())), "crisp": crisp}
