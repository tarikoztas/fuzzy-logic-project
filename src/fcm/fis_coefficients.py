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


def build_fis(shape: str = "tri", defuzz: str = "centroid", kind: str = "mamdani") -> FIS:
    ins = [Variable("Dev", (0.0, 1.0), input_terms(shape)), Variable("Dis", (0.0, 1.0), input_terms(shape))]
    outs = [Variable(n, (0.0, 1.0), output_terms(shape)) for n in ("alpha", "beta", "gamma")]
    rules = [Rule({"Dev": dev, "Dis": dis}, dict(zip(("alpha", "beta", "gamma"), cons)))
             for (dev, dis), cons in RULE_TABLE.items()]
    return FIS(ins, outs, rules, kind=kind, defuzz=defuzz)


def fis_inputs(y: np.ndarray, xi: np.ndarray, theta: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return np.abs(y - 0.5 * (xi + theta)), np.abs(xi - theta)


class FuzzyCoefficients:
    """Coefficient provider for src/fcm/pipeline.py: fis(y, xi, theta) -> (alpha, beta, gamma)."""

    def __init__(self, shape: str = "tri", defuzz: str = "centroid", kind: str = "mamdani",
                 normalize: bool = True, mode: str = "full", k: float = 15.0, variant: str = "signed"):
        if mode not in ("full", "split"):
            raise ValueError("mode must be 'full' or 'split'")
        self.fis = build_fis(shape, defuzz, kind)
        self.normalize, self.mode, self.k, self.variant = normalize, mode, k, variant
        self.label = (f"FIS-{mode}-{kind}-{shape}-{defuzz if kind == 'mamdani' else 'wavg'}"
                      + ("" if normalize or mode == "split" else "-raw"))

    def __call__(self, y, xi, theta):
        if xi is None or theta is None:
            raise ValueError("the fuzzy coefficient system needs both xi and theta")
        dev, dis = fis_inputs(y, xi, theta)
        out = self.fis.evaluate(Dev=dev, Dis=dis)
        a, b, g = (out[k].reshape(np.shape(y)) for k in ("alpha", "beta", "gamma"))
        if self.mode == "split":
            from .adaptive_params import paper_coefficients
            ap, bp, gp = paper_coefficients(y, xi, theta, k=self.k, variant=self.variant)
            share = b / (b + g)
            return ap, (bp + gp) * share, (bp + gp) * (1.0 - share)
        if self.normalize:
            s = a + b + g
            a, b, g = a / s, b / s, g / s
        return a, b, g
