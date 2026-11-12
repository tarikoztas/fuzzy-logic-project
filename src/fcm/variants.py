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


def kwargs_for(name: str) -> dict:
    """run_asrfcm keyword arguments for a variant name (ABLATION or FIS_VARIANTS)."""
    if name in ABLATION:
        return {**PAPER, **ABLATION[name]}
    if name in FIS_VARIANTS:
        return {**PAPER, "coeff_method": "fis", "fis": FuzzyCoefficients(**FIS_VARIANTS[name])}
    raise KeyError(name)
