"""Proposed extension (D-033, CP4): alpha, beta, gamma from an explicit fuzzy
inference system instead of the paper's closed form (Eqs. 15-19).

Inputs per pixel (gray values in [0, 1]):
    Dev = |y - (xi + theta) / 2|   how far the pixel is from the consensus of the
                                   two corrected estimates   (large -> probably noise)
    Dis = |xi - theta|             how much the two estimates disagree
                                   (large -> probably an edge, where the mean-like
                                   non-local estimate is blurred, D-038)
Outputs: alpha (trust in y), beta (trust in xi), gamma (trust in theta).

Rule base (CP4, fixed before the experiments):
                 Dis Small            Dis Medium            Dis Large
    Dev Small    a High  b Med g Med  a High b Med g Low    a High b Med  g Low
    Dev Medium   a Med   b Med g High a Med  b High g Med   a Med  b High g Low
    Dev Large    a Low   b High g High a Low b High g Med   a Low  b High g Low

Variants: membership shape ("tri" | "gauss"), defuzzification ("centroid" |
"bisector" | "mom"), inference ("mamdani" | "sugeno"), per-pixel normalisation
alpha + beta + gamma = 1 (default on).

Modes:
  "full"  - the pre-registered design (CP4): the FIS gives all three coefficients.
  "split" - post-hoc, exploratory (D-041, added after the first results showed that
            "full" trusts the noisy pixel far more than the paper: alpha share ~30 %
            vs ~0.1 %): alpha and the total trust beta + gamma are taken from the
            paper's formula, the FIS only decides how that trust is split between
            xi and theta:  beta = (beta_p + gamma_p) * b / (b + g), gamma likewise.
"""
from __future__ import annotations

import numpy as np

from src.fuzzy import FIS, MF, Rule, Variable

INPUT_TERMS = ("Small", "Medium", "Large")
OUTPUT_TERMS = ("Low", "Medium", "High")

# (Dev term, Dis term) -> (alpha, beta, gamma) terms
RULE_TABLE = {
    ("Small", "Small"): ("High", "Medium", "Medium"),
    ("Small", "Medium"): ("High", "Medium", "Low"),
    ("Small", "Large"): ("High", "Medium", "Low"),
    ("Medium", "Small"): ("Medium", "Medium", "High"),
    ("Medium", "Medium"): ("Medium", "High", "Medium"),
    ("Medium", "Large"): ("Medium", "High", "Low"),
    ("Large", "Small"): ("Low", "High", "High"),
    ("Large", "Medium"): ("Low", "High", "Medium"),
    ("Large", "Large"): ("Low", "High", "Low"),
}


def input_terms(shape: str) -> dict[str, MF]:
    if shape == "tri":
        return {"Small": MF("tri", 0.0, 0.0, 0.15), "Medium": MF("tri", 0.05, 0.2, 0.35),
                "Large": MF("trap", 0.2, 0.4, 1.0, 1.0)}
    if shape == "gauss":  # same 0.5-crossing points as the triangular sets
        return {"Small": MF("gauss_left", 0.0, 0.0637), "Medium": MF("gauss", 0.2, 0.0637),
                "Large": MF("gauss_right", 0.4, 0.0849)}
    raise ValueError("shape must be 'tri' or 'gauss'")


def output_terms(shape: str) -> dict[str, MF]:
    if shape == "tri":
        return {"Low": MF("tri", 0.0, 0.0, 0.5), "Medium": MF("tri", 0.25, 0.5, 0.75),
                "High": MF("tri", 0.5, 1.0, 1.0)}
    if shape == "gauss":
        return {"Low": MF("gauss_left", 0.0, 0.2123), "Medium": MF("gauss", 0.5, 0.1062),
                "High": MF("gauss_right", 1.0, 0.2123)}
    raise ValueError("shape must be 'tri' or 'gauss'")


# Second iteration, candidate B (D-044/D-045): an impulse input Imp = |y - median3x3(y)|.
# Imp is Small -> the 9 rules above apply unchanged; Imp is Large (the pixel is an outlier
# among its 3x3 neighbours, typical of salt-and-pepper) -> do not trust the pixel.
IMP_TERMS = {"Small": MF("trap", 0.0, 0.0, 0.05, 0.2), "Large": MF("trap", 0.05, 0.2, 1.0, 1.0)}
IMP_LARGE_RULES = {"Small": ("Low", "High", "High"), "Medium": ("Low", "High", "Medium"),
                   "Large": ("Low", "High", "Low")}   # Dis term -> (alpha, beta, gamma)


def build_fis(shape: str = "tri", defuzz: str = "centroid", kind: str = "mamdani", imp: bool = False) -> FIS:
    ins = [Variable("Dev", (0.0, 1.0), input_terms(shape)), Variable("Dis", (0.0, 1.0), input_terms(shape))]
    outs = [Variable(n, (0.0, 1.0), output_terms(shape)) for n in ("alpha", "beta", "gamma")]
    names = ("alpha", "beta", "gamma")
    if not imp:
        rules = [Rule({"Dev": dev, "Dis": dis}, dict(zip(names, cons))) for (dev, dis), cons in RULE_TABLE.items()]
        return FIS(ins, outs, rules, kind=kind, defuzz=defuzz)
    ins.append(Variable("Imp", (0.0, 1.0), IMP_TERMS))
    rules = [Rule({"Imp": "Small", "Dev": dev, "Dis": dis}, dict(zip(names, cons)))
             for (dev, dis), cons in RULE_TABLE.items()]
    rules += [Rule({"Imp": "Large", "Dis": dis}, dict(zip(names, cons))) for dis, cons in IMP_LARGE_RULES.items()]
    return FIS(ins, outs, rules, kind=kind, defuzz=defuzz)


def impulse_input(y: np.ndarray) -> np.ndarray:
    """Imp = |y - median3x3(y)|; colour: root-mean-square over the channels (as Dev/Dis, D-043)."""
    from scipy.ndimage import median_filter

    y = np.asarray(y, dtype=np.float64)
    if y.ndim == 3:
        d = np.stack([y[..., c] - median_filter(y[..., c], size=3, mode="mirror") for c in range(y.shape[-1])], -1)
        return np.sqrt((d**2).mean(axis=-1))
    return np.abs(y - median_filter(y, size=3, mode="mirror"))


def fis_inputs(y: np.ndarray, xi: np.ndarray, theta: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Dev and Dis; for colour images (H, W, C) the root-mean-square over the channels (D-043)."""
    dev, dis = y - 0.5 * (xi + theta), xi - theta
    if np.ndim(dev) == 3:
        return np.sqrt((dev**2).mean(axis=-1)), np.sqrt((dis**2).mean(axis=-1))
    return np.abs(dev), np.abs(dis)


class FuzzyCoefficients:
    """Coefficient provider for src/fcm/pipeline.py: fis(y, xi, theta) -> (alpha, beta, gamma)."""

    def __init__(self, shape: str = "tri", defuzz: str = "centroid", kind: str = "mamdani",
                 normalize: bool = True, mode: str = "full", k: float = 15.0, variant: str = "signed",
                 alpha_scale: float = 1.0, imp: bool = False):
        """alpha_scale (candidate A, second iteration): the FIS alpha is multiplied by this factor
        before normalisation, i.e. the alpha output universe becomes [0, alpha_scale]. The paper's
        formula gives the noisy pixel ~0.1 % of the trust, FIS-full ~30 % (D-041).
        imp (candidate B): add the impulse input Imp (see IMP_TERMS)."""
        if mode not in ("full", "split"):
            raise ValueError("mode must be 'full' or 'split'")
        if not 0.0 < alpha_scale <= 1.0:
            raise ValueError("alpha_scale must be in (0, 1]")
        self.fis = build_fis(shape, defuzz, kind, imp=imp)
        self.normalize, self.mode, self.k, self.variant = normalize, mode, k, variant
        self.alpha_scale, self.imp = alpha_scale, imp
        self.label = (f"FIS-{mode}-{kind}-{shape}-{defuzz if kind == 'mamdani' else 'wavg'}"
                      + ("" if normalize or mode == "split" else "-raw")
                      + ("" if alpha_scale == 1.0 else f"-a{alpha_scale:g}") + ("-imp" if imp else ""))

    def __call__(self, y, xi, theta):
        if xi is None or theta is None:
            raise ValueError("the fuzzy coefficient system needs both xi and theta")
        dev, dis = fis_inputs(y, xi, theta)
        extra = {"Imp": impulse_input(y)} if self.imp else {}
        out = self.fis.evaluate(Dev=dev, Dis=dis, **extra)
        a, b, g = (out[k].reshape(np.shape(dev)) for k in ("alpha", "beta", "gamma"))
        if self.mode == "split":
            from .adaptive_params import paper_coefficients
            ap, bp, gp = paper_coefficients(y, xi, theta, k=self.k, variant=self.variant)
            share = b / (b + g)
            return ap, (bp + gp) * share, (bp + gp) * (1.0 - share)
        a = a * self.alpha_scale
        if self.normalize:
            s = a + b + g
            a, b, g = a / s, b / s, g / s
        return a, b, g
