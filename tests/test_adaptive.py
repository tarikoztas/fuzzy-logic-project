import numpy as np
import pytest

from src.data import noise, synthetic
from src.fcm.adaptive_params import absolute_differences, paper_coefficients
from src.fcm.local_info import local_spatial_info


def test_hand_example():
    y, xi, th = np.array([0.5]), np.array([0.5]), np.array([0.3])
    a, b, g = paper_coefficients(y, xi, th, k=15.0, eps=0.0)
    assert b[0] == pytest.approx(15.0)                 # 15 * exp(0)
    assert g[0] == pytest.approx(15.0 * np.exp(0.2))
    assert a[0] == pytest.approx(1 / (b[0] + g[0]))


def test_positive_and_bounded():
    rng = np.random.default_rng(0)
    y, xi, th = rng.random((3, 50, 50))
    for variant in ("signed", "abs"):
        a, b, g = paper_coefficients(y, xi, th, variant=variant)
        assert (a > 0).all() and (b > 0).all() and (g > 0).all()
        assert b.min() >= 15 / np.e - 1e-9 and b.max() <= 15 * np.e + 1e-9


def test_signed_variant_is_asymmetric_abs_is_not():
    y, xi = np.array([0.8, 0.2]), np.array([0.5, 0.5])  # salt-like and pepper-like deviation
    _, b_signed, _ = paper_coefficients(y, xi, xi, variant="signed")
    _, b_abs, _ = paper_coefficients(y, xi, xi, variant="abs")
    assert b_signed[0] > 15 > b_signed[1]
    assert b_abs[0] == pytest.approx(b_abs[1])


def test_more_noise_lowers_alpha():
    s = synthetic.load("sy2")
    means = []
    for p in (0.01, 0.15):
        y = noise.add_noise(s.image, "mixed", p, seed=0)
        xi = local_spatial_info(y)
        a, b, g = paper_coefficients(y, xi, xi, variant="abs")
        means.append((a.mean(), (b + g).mean()))
    assert means[1][0] < means[0][0] and means[1][1] > means[0][1]


def test_absolute_differences():
    d1, d2 = absolute_differences(np.array([0.2]), np.array([0.5]), np.array([0.1]), eps=0.0)
    assert d1[0] == pytest.approx(0.3) and d2[0] == pytest.approx(0.1)
