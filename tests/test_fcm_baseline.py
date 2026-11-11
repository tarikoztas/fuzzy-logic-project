import numpy as np
import pytest

from src.data import synthetic
from src.eval.metrics import accuracy
from src.fcm.baseline_fcm import fcm, init_membership, update_memberships


def test_init_membership_columns_sum_to_one_and_seeded():
    U = init_membership(3, 100, seed=1)
    assert U.shape == (3, 100)
    assert np.allclose(U.sum(axis=0), 1.0)
    assert np.array_equal(U, init_membership(3, 100, seed=1))


def test_membership_formula_hand_example():
    # one pixel, distances 0.1 and 0.3 to two centers, m = 2:
    # u_1 = 1 / (1 + (0.1/0.3)^2) = 0.9 ; u_2 = 0.1
    d2 = np.array([[0.1**2], [0.3**2]])
    assert np.allclose(update_memberships(d2, 2.0).ravel(), [0.9, 0.1])


def test_pixel_on_center_gets_full_membership():
    U = update_memberships(np.array([[0.0], [0.25]]), 2.0)
    assert U[0, 0] == pytest.approx(1.0)


def test_two_clear_groups():
    img = np.array([[0.1, 0.1, 0.1, 0.9, 0.9, 0.9]])
    res = fcm(img, K=2, seed=0)
    assert np.allclose(np.sort(res.centers), [0.1, 0.9], atol=1e-6)
    assert np.allclose(res.U.sum(axis=0), 1.0)
    assert res.U.shape == (2, 1, 6)


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_objective_never_increases(seed):
    s = synthetic.load("sy3")
    noisy = s.image + np.random.default_rng(seed).normal(0, 0.1, s.image.shape)
    res = fcm(np.clip(noisy, 0, 1), K=3, seed=seed)
    J = np.array(res.J_history)
    assert np.all(np.diff(J) <= 1e-9 * J[:-1])  # FCM is a descent method (alternating optimization)
    assert res.n_iter <= 100


def test_noise_free_synthetic_is_perfect():
    for name in synthetic.NAMES:
        s = synthetic.load(name)
        res = fcm(s.image, K=s.K, seed=0)
        assert accuracy(s.labels, res.labels) == pytest.approx(100.0)
        levels = np.asarray(synthetic.LEVELS[name]) / 255
        assert np.allclose(np.sort(res.centers), levels, atol=1e-4)


def test_same_seed_same_result():
    s = synthetic.load("sy2")
    a, b = fcm(s.image, 3, seed=5), fcm(s.image, 3, seed=5)
    assert np.array_equal(a.U, b.U) and a.n_iter == b.n_iter
