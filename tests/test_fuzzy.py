"""Tests of the fuzzy inference toolkit and of the fuzzy coefficient system (D-033)."""
import numpy as np
import pytest

from src.fcm.fis_coefficients import RULE_TABLE, FuzzyCoefficients, build_fis
from src.fuzzy import FIS, MF, Rule, Variable, gaussmf, trapmf, trimf
from src.fuzzy.defuzz import bisector, centroid, mean_of_maxima


def test_membership_functions():
    assert trimf(np.array([0, 0.1, 0.2, 0.3, 0.4]), 0.0, 0.2, 0.4).tolist() == pytest.approx([0, 0.5, 1, 0.5, 0])
    assert trimf(np.array([0.0, 0.075, 0.2]), 0.0, 0.0, 0.15).tolist() == pytest.approx([1, 0.5, 0])  # shoulder
    assert trapmf(np.array([0.1, 0.3, 0.5, 0.9]), 0.2, 0.4, 1, 1).tolist() == pytest.approx([0, 0.5, 1, 1])
    assert gaussmf(np.array([0.5]), 0.5, 0.1)[0] == 1.0
    assert MF("gauss_left", 0.0, 0.0637)(np.array([0.075]))[0] == pytest.approx(0.5, abs=0.01)


def test_defuzzification_known_cases():
    z = np.linspace(0, 1, 1001)
    sym = trimf(z, 0.2, 0.5, 0.8)[None, :]               # symmetric triangle
    assert centroid(z, sym)[0] == pytest.approx(0.5, abs=1e-3)
    assert bisector(z, sym)[0] == pytest.approx(0.5, abs=2e-3)
    assert mean_of_maxima(z, sym)[0] == pytest.approx(0.5, abs=1e-3)
    ramp = trimf(z, 0.0, 1.0, 1.0)[None, :]              # mu(z) = z
    assert centroid(z, ramp)[0] == pytest.approx(2 / 3, abs=2e-3)
    assert bisector(z, ramp)[0] == pytest.approx(np.sqrt(0.5), abs=2e-3)
    assert mean_of_maxima(z, ramp)[0] == pytest.approx(1.0)
    plateau = np.minimum(trapmf(z, 0.0, 0.2, 0.6, 0.8), 0.7)[None, :]
    assert mean_of_maxima(z, plateau)[0] == pytest.approx(0.4, abs=2e-3)
    assert centroid(z, np.zeros((1, z.size)))[0] == 0.5   # no rule fired


def tiny_fis(kind="mamdani"):
    t = {"lo": MF("tri", 0, 0, 1), "hi": MF("tri", 0, 1, 1)}
    x = Variable("x", (0, 1), t)
    out = Variable("o", (0, 1), {"lo": MF("tri", 0, 0, 0.5), "hi": MF("tri", 0.5, 1, 1)})
    rules = [Rule({"x": "lo"}, {"o": "lo"}), Rule({"x": "hi"}, {"o": "hi"})]
    return FIS([x], [out], rules, kind=kind)


def test_mamdani_hand_example():
    # x = 0.25: rule1 fires 0.75 (lo), rule2 fires 0.25 (hi); output must lean to "lo"
    r = tiny_fis().evaluate(x=np.array([0.0, 0.25, 0.5, 1.0]))["o"]
    assert r[0] < r[1] < r[2] < r[3]
    assert r[2] == pytest.approx(0.5, abs=1e-3)             # symmetric firing -> middle


def test_sugeno_weighted_average():
    f = tiny_fis("sugeno")
    lo, hi = f.sugeno_constants["o"]["lo"], f.sugeno_constants["o"]["hi"]
    assert lo == pytest.approx(1 / 6, abs=2e-3) and hi == pytest.approx(5 / 6, abs=2e-3)  # term centroids
    r = f.evaluate(x=np.array([0.25]))["o"][0]
    assert r == pytest.approx(0.75 * lo + 0.25 * hi)


def test_rule_validation():
    x = Variable("x", (0, 1), {"lo": MF("tri", 0, 0, 1)})
    with pytest.raises(ValueError):
        FIS([x], [x], [Rule({"x": "missing"}, {"x": "lo"})])


def test_rule_base_complete_and_readable():
    f = build_fis()
    assert len(f.rules) == 9 and len(RULE_TABLE) == 9
    assert f.rule_table()[0] == "R1: IF Dev is Small AND Dis is Small THEN alpha is High, beta is Medium, gamma is Medium"


def test_firing_strengths_partition():
    # with triangular input sets every value belongs to at most two neighbouring terms
    f = build_fis()
    w = f.firing_strengths({"Dev": np.array([0.1]), "Dis": np.array([0.0])})
    assert (w > 0).sum() == 2


@pytest.mark.parametrize("shape", ["tri", "gauss"])
@pytest.mark.parametrize("defuzz", ["centroid", "bisector", "mom"])
def test_coefficients_behave_as_the_rules_say(shape, defuzz):
    fc = FuzzyCoefficients(shape=shape, defuzz=defuzz)
    y = np.array([0.50, 1.00, 0.50, 1.00])
    xi = np.array([0.50, 0.50, 0.50, 0.50])
    th = np.array([0.50, 0.50, 0.95, 0.95])
    a, b, g = fc(y, xi, th)
    assert np.allclose(a + b + g, 1.0)
    # consistent pixel in a flat region: alpha largest
    assert a[0] > b[0] and a[0] > g[0]
    # strong outlier in a flat region: alpha smallest
    assert a[1] < b[1] and a[1] < g[1]
    # estimates disagree (edge): trust xi more than theta
    assert b[2] > g[2] and b[3] > g[3]


def test_sugeno_close_to_mamdani_centroid():
    rng = np.random.default_rng(0)
    y, xi, th = rng.random((3, 500))
    m = FuzzyCoefficients(kind="mamdani")(y, xi, th)
    s = FuzzyCoefficients(kind="sugeno")(y, xi, th)
    assert max(np.abs(a - b).max() for a, b in zip(m, s)) < 0.15


def test_needs_both_corrected_images():
    with pytest.raises(ValueError):
        FuzzyCoefficients()(np.zeros(3), None, np.zeros(3))


def test_split_mode_keeps_paper_alpha_and_total_trust():
    from src.fcm.adaptive_params import paper_coefficients
    rng = np.random.default_rng(1)
    y, xi, th = rng.random((3, 300))
    a, b, g = FuzzyCoefficients(mode="split")(y, xi, th)
    ap, bp, gp = paper_coefficients(y, xi, th)
    assert np.allclose(a, ap) and np.allclose(b + g, bp + gp)
    assert ((b > 0) & (g > 0)).all()
