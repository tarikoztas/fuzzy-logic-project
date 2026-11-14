"""Named method variants for the experiments (one factor changes at a time).

Every variant is a set of keyword arguments for src/fcm/pipeline.run_asrfcm, so
baseline and extensions share exactly the same code path. "paper" is the
reproduced method with the paper's settings; all others differ from it in one
factor only (C2 ablation, D-006-final) or in the coefficient rule (FIS, D-033/D-041).
"""
from __future__ import annotations

from .fis_coefficients import FuzzyCoefficients

PAPER = dict(coeff_method="paper", coeff_variant="signed", empty_col_policy="keep")

# C2: single-factor ablation of under-specified or arbitrary choices of the paper
ABLATION = {
    "paper": {},
    "ratio=0.5": dict(ratio=0.5),
    "ratio=0.7": dict(ratio=0.7),
    "ratio=0.8": dict(ratio=0.8),
    "rounding=ceil": dict(rounding="ceil"),
    "dG=abs": dict(coeff_variant="abs"),
    "sigma=0.6": dict(sigma=0.6),
    "sigma=0.9": dict(sigma=0.9),
    "empty=argmax": dict(empty_col_policy="argmax"),
    "nlm_scale=255": dict(nlm_scale=255.0),
}

# Contribution: fuzzy-rule coefficient systems
FIS_VARIANTS = {
    "FIS-full (pre-registered)": dict(mode="full"),
    "FIS-split (post-hoc)": dict(mode="split"),
    "FIS-full gauss": dict(mode="full", shape="gauss"),
    "FIS-full bisector": dict(mode="full", defuzz="bisector"),
    "FIS-full mom": dict(mode="full", defuzz="mom"),
    "FIS-full sugeno": dict(mode="full", kind="sugeno"),
    "FIS-full unnormalised": dict(mode="full", normalize=False),
    "FIS-split gauss": dict(mode="split", shape="gauss"),
    "FIS-split bisector": dict(mode="split", defuzz="bisector"),
    "FIS-split mom": dict(mode="split", defuzz="mom"),
    "FIS-split sugeno": dict(mode="split", kind="sugeno"),
}


# Second iteration (D-044/D-045). Candidates A/B change the coefficient FIS, C adds a fuzzy
# rule for the reward factor sigma (src/fcm/fis_sigma.py). Their settings are given in the
# tuning/test configs (experiments/contribution/tuning.yaml, second_iteration.yaml).
SECOND = {
    "sigma=0.9 (fixed)": dict(sigma=0.9),   # control: a larger but fixed reward factor
}
# Selected after tuning (D-045): FIS-sigma (primary, T7) and FIS-sigma+A (secondary, T8).
FIS_SIGMA = dict(level="image", breaks=(0.05, 0.15, 0.25), out=(0.3, 0.6, 0.95))
FIS_SIGMA_A = dict(level="image", breaks=(0.05, 0.15, 0.25), out=(0.3, 0.6, 0.9))


def kwargs_for(name: str) -> dict:
    """run_asrfcm keyword arguments for a variant name (ABLATION, FIS_VARIANTS or SECOND)."""
    if name in ABLATION:
        return {**PAPER, **ABLATION[name]}
    if name in FIS_VARIANTS:
        return {**PAPER, "coeff_method": "fis", "fis": FuzzyCoefficients(**FIS_VARIANTS[name])}
    if name in SECOND:
        return {**PAPER, **SECOND[name]}
    if name == "FIS-sigma":
        from .fis_sigma import FuzzySigma
        return {**PAPER, "sigma_rule": FuzzySigma(**FIS_SIGMA)}
    if name == "FIS-sigma+A":
        from .fis_sigma import FuzzySigma
        return {**PAPER, "sigma_rule": FuzzySigma(**FIS_SIGMA_A), "coeff_method": "fis",
                "fis": FuzzyCoefficients(mode="full", alpha_scale=0.002)}
    raise KeyError(name)
