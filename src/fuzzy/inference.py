"""A small, vectorised fuzzy inference engine (Mamdani and zero-order Sugeno).

Pipeline for N input samples at once:
  1. fuzzification   - degree of every input term,            mu_term(x)       (N,)
  2. rule firing     - AND of the antecedents = min,           w_r              (N,)
  3. implication     - clip each consequent set at w_r (min),  min(w_r, mu_out) (N, U)
  4. aggregation     - union over rules = max,                                  (N, U)
  5. defuzzification - centroid / bisector / mean of maxima,                    (N,)
Sugeno (zero-order): every consequent term is a constant c_t; output = sum(w_r c_r) / sum(w_r).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .defuzz import METHODS
from .membership import MF


@dataclass
class Variable:
    name: str
    universe: tuple[float, float]
    terms: dict[str, MF]
    resolution: int = 201  # samples of the universe for output variables

    def grid(self) -> np.ndarray:
        return np.linspace(self.universe[0], self.universe[1], self.resolution)

    def fuzzify(self, x: np.ndarray) -> dict[str, np.ndarray]:
        x = np.clip(np.asarray(x, dtype=np.float64), *self.universe)
        return {t: mf(x) for t, mf in self.terms.items()}


@dataclass
class Rule:
    antecedent: dict[str, str]   # {input variable: term}, joined with AND
    consequent: dict[str, str]   # {output variable: term}

    def text(self) -> str:
        a = " AND ".join(f"{v} is {t}" for v, t in self.antecedent.items())
        c = ", ".join(f"{v} is {t}" for v, t in self.consequent.items())
        return f"IF {a} THEN {c}"


@dataclass
class FIS:
    inputs: list[Variable]
    outputs: list[Variable]
    rules: list[Rule]
    kind: str = "mamdani"                       # "mamdani" or "sugeno"
    defuzz: str = "centroid"                    # Mamdani only
    sugeno_constants: dict[str, dict[str, float]] = field(default_factory=dict)  # output -> term -> c
    chunk: int = 16384                          # pixels per block (memory bound for the (N, U) arrays)

    def __post_init__(self):
        names = {v.name for v in self.inputs}
        outs = {v.name: v for v in self.outputs}
        for r in self.rules:
            for v, t in r.antecedent.items():
                var = next((i for i in self.inputs if i.name == v), None)
                if var is None or t not in var.terms:
                    raise ValueError(f"bad antecedent {v} is {t}")
            for v, t in r.consequent.items():
                if v not in outs or t not in outs[v].terms:
                    raise ValueError(f"bad consequent {v} is {t}")
        if not names:
            raise ValueError("no inputs")
        if self.kind not in ("mamdani", "sugeno"):
            raise ValueError("kind must be 'mamdani' or 'sugeno'")
        if self.defuzz not in METHODS:
            raise ValueError(f"defuzz must be one of {tuple(METHODS)}")
        if self.kind == "sugeno" and not self.sugeno_constants:
            self.sugeno_constants = {o.name: {t: float(centroid_of(o, t)) for t in o.terms} for o in self.outputs}

    # ---- steps ----
    def firing_strengths(self, x: dict[str, np.ndarray]) -> np.ndarray:
        """(R, N) rule activations: min over each rule's antecedent memberships."""
        fz = {v.name: v.fuzzify(x[v.name]) for v in self.inputs}
        return np.stack([np.minimum.reduce([fz[v][t] for v, t in r.antecedent.items()]) for r in self.rules])

    def aggregate(self, w: np.ndarray, out: Variable) -> tuple[np.ndarray, np.ndarray]:
        """Aggregated output set (N, U) for one output variable (Mamdani)."""
        z = out.grid()
        mus = {t: mf(z) for t, mf in out.terms.items()}
        agg = np.zeros((w.shape[1], z.size))
        for r, wr in zip(self.rules, w):
            if out.name in r.consequent:
                np.maximum(agg, np.minimum(wr[:, None], mus[r.consequent[out.name]][None, :]), out=agg)
        return z, agg

    def evaluate(self, **x: np.ndarray) -> dict[str, np.ndarray]:
        """Crisp outputs for N samples (inputs given as keyword arrays of equal length)."""
        n = np.asarray(next(iter(x.values()))).size
        flat = {k: np.asarray(v, dtype=np.float64).ravel() for k, v in x.items()}
        result = {o.name: np.empty(n) for o in self.outputs}
        for s in range(0, n, self.chunk):
            part = {k: v[s : s + self.chunk] for k, v in flat.items()}
            w = self.firing_strengths(part)
            for o in self.outputs:
                if self.kind == "mamdani":
                    z, agg = self.aggregate(w, o)
                    result[o.name][s : s + self.chunk] = METHODS[self.defuzz](z, agg)
                else:
                    c = np.array([self.sugeno_constants[o.name][r.consequent[o.name]] for r in self.rules])
                    tot = w.sum(axis=0)
                    val = (c[:, None] * w).sum(axis=0) / np.where(tot > 0, tot, 1.0)
                    result[o.name][s : s + self.chunk] = np.where(tot > 0, val, 0.5 * sum(o.universe))
        return result

    def rule_table(self) -> list[str]:
        return [f"R{i + 1}: {r.text()}" for i, r in enumerate(self.rules)]


def centroid_of(var: Variable, term: str) -> float:
    z = var.grid()
    mu = var.terms[term](z)
    return float((z * mu).sum() / mu.sum())
