"""Second iteration of the contribution (D-044/D-045): fuzzy sigma, bounded alpha, impulse input."""
import numpy as np
import pytest

from src.fcm.fis_coefficients import FuzzyCoefficients, impulse_input
from src.fcm.fis_sigma import FuzzySigma, build_sigma_fis, local_noise, noise_estimate
from src.fcm.local_info import local_spatial_info
from src.fcm.pipeline import run_asrfcm


def test_sigma_fis_endpoints_and_monotone():
    fis = build_sigma_fis((0.05, 0.15, 0.25), (0.3, 0.6, 0.9))
    x = np.linspace(0, 0.5, 51)
    s = fis.evaluate(Noise=x)["Sigma"]
    assert s[0] == pytest.approx(0.3, abs=1e-6)        # only "Low" fires -> centre of Small
    assert s[15] == pytest.approx(0.6, abs=1e-6)       # only "Medium" fires at its peak
    assert s[-1] == pytest.approx(0.9, abs=1e-6)       # only "High" fires
    assert np.all(np.diff(s) >= -1e-9)                 # noisier image -> never a smaller sigma


def test_noise_estimate_flat_and_gaussian():
    assert noise_estimate(np.full((64, 64), 0.4)) == 0.0
    rng = np.random.default_rng(0)
    est = noise_estimate(0.5 + rng.normal(0, 0.05, (256, 256)))
    assert est == pytest.approx(0.05, rel=0.05)        # MAD estimator recovers the std


def test_local_noise_zero_on_flat_image():
    assert np.all(local_noise(np.full((20, 20), 0.7)) == 0.0)


def test_per_pixel_sigma_equals_scalar_when_constant():
    rng = np.random.default_rng(1)
    img = rng.random((24, 24))
    a = local_spatial_info(img, 5, 0.3)
    b = local_spatial_info(img, 5, np.full(img.shape, 0.3))
    assert np.allclose(a, b)
    with pytest.raises(ValueError):
        local_spatial_info(img, 5, np.full((3, 3), 0.3))
    with pytest.raises(ValueError):
        local_spatial_info(img, 5, np.full(img.shape, 1.0))


def test_sigma_rule_constant_matches_default():
    rng = np.random.default_rng(2)
    img = np.clip(np.kron([[0.2, 0.8], [0.8, 0.2]], np.ones((12, 12))) + rng.normal(0, 0.05, (24, 24)), 0, 1)
    r0 = run_asrfcm(img, 2, seed=0, use_cache=False)
    r1 = run_asrfcm(img, 2, seed=0, use_cache=False, sigma_rule=lambda y: 0.3)
    assert np.allclose(r0.result.U, r1.result.U)
    assert r1.sigma_used == 0.3
    r2 = run_asrfcm(img, 2, seed=0, use_cache=False, sigma_rule=FuzzySigma(level="pixel"))
    assert 0.3 <= r2.sigma_used <= 0.9


def test_alpha_scale_one_is_default_and_shrinks_alpha_share():
    rng = np.random.default_rng(3)
    y, xi, th = rng.random((3, 16, 16))
    base = FuzzyCoefficients(mode="full")(y, xi, th)
    same = FuzzyCoefficients(mode="full", alpha_scale=1.0)(y, xi, th)
    for u, v in zip(base, same):
        assert np.allclose(u, v)
    a, b, g = FuzzyCoefficients(mode="full", alpha_scale=0.002)(y, xi, th)
    assert np.all(a / (a + b + g) < base[0] / sum(base))
    with pytest.raises(ValueError):
        FuzzyCoefficients(alpha_scale=0.0)


def test_impulse_input_and_rules():
    flat = np.full((10, 10), 0.5)
    spike = flat.copy(); spike[5, 5] = 1.0
    imp = impulse_input(spike)
    assert imp[5, 5] == pytest.approx(0.5) and imp[0, 0] == 0.0
    xi = th = np.full_like(flat, 0.5)
    # no impulse anywhere -> Imp is fully "Small" and the 3-input system equals the 2-input one
    a1 = FuzzyCoefficients(mode="full", imp=True)(flat, xi, th)
    a0 = FuzzyCoefficients(mode="full")(flat, xi, th)
    for u, v in zip(a0, a1):
        assert np.allclose(u, v)
    # an impulse that the corrected images did not remove (Dev = 0, so the 2-input system trusts it)
    # gets less trust in its own value once Imp is an input
    w1 = FuzzyCoefficients(mode="full", imp=True)(spike, spike, spike)
    w0 = FuzzyCoefficients(mode="full")(spike, spike, spike)
    assert w1[0][5, 5] < w0[0][5, 5]
