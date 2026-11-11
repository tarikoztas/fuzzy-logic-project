import numpy as np
import pytest

from src.data.noise import KINDS, add_noise, gaussian, salt_pepper, speckle

FLAT = np.full((200, 200), 0.5)


@pytest.mark.parametrize("kind", KINDS)
def test_same_seed_same_noise_and_range(kind):
    a = add_noise(FLAT, kind, 0.05, seed=3)
    b = add_noise(FLAT, kind, 0.05, seed=3)
    c = add_noise(FLAT, kind, 0.05, seed=4)
    assert np.array_equal(a, b)
    assert not np.array_equal(a, c)
    assert a.min() >= 0.0 and a.max() <= 1.0
    assert a.shape == FLAT.shape


def test_zero_level_is_identity():
    assert np.array_equal(add_noise(FLAT, "mixed", 0.0, seed=0), FLAT)


def test_salt_pepper_density():
    rng = np.random.default_rng(0)
    out = salt_pepper(FLAT, 0.10, rng)
    changed = out != FLAT
    assert changed.mean() == pytest.approx(0.10, abs=0.01)
    assert (out[changed] == 0).mean() == pytest.approx(0.5, abs=0.05)  # half pepper, half salt


def test_gaussian_variance():
    rng = np.random.default_rng(0)
    out = gaussian(FLAT, 0.01, rng)  # std 0.1, clipping negligible around 0.5
    assert np.var(out - FLAT) == pytest.approx(0.01, rel=0.05)
    assert np.mean(out - FLAT) == pytest.approx(0.0, abs=0.005)


def test_speckle_is_multiplicative():
    rng = np.random.default_rng(0)
    img = np.zeros((200, 200))
    img[:, 100:] = 0.4
    out = speckle(img, 0.05, rng)
    assert np.all(out[:, :100] == 0)  # black pixels untouched (n * 0 = 0)
    rel = (out[:, 100:] - 0.4) / 0.4
    assert np.var(rel) == pytest.approx(0.05, rel=0.05)


def test_rejects_bad_input():
    with pytest.raises(ValueError):
        add_noise(FLAT, "poisson", 0.05, 0)
    with pytest.raises(ValueError):
        add_noise(FLAT, "mixed", 5, 0)  # percent instead of fraction
    with pytest.raises(ValueError):
        add_noise(FLAT * 255, "mixed", 0.05, 0)
