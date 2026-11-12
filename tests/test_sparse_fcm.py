import numpy as np
import pytest

from src.data import noise, synthetic
from src.eval.metrics import accuracy
from src.fcm.baseline_fcm import fcm
from src.fcm.pipeline import run_asrfcm
from src.fcm.sparse_fcm import sparse_fcm


def noisy(name, p=0.05, seed=0):
    s = synthetic.load(name)
    return s, noise.add_noise(s.image, "mixed", p, seed)


@pytest.mark.parametrize("policy", ["keep", "argmax"])
def test_columns_sum_to_one_no_nan(policy):
    s, y = noisy("sy3")
    r = run_asrfcm(y, s.K, seed=1, empty_col_policy=policy, use_cache=False).result
    assert np.isfinite(r.U).all()
    assert np.allclose(r.U.sum(axis=0), 1.0)
    assert r.n_iter <= 100


def test_argmax_policy_gives_crisp_partition():
    # sqrt(0.4) = 0.632 > 0.5: at most one membership survives per pixel
    s, y = noisy("sy2")
    U = run_asrfcm(y, s.K, empty_col_policy="argmax", use_cache=False).result.U
    assert set(np.unique(U)) <= {0.0, 1.0}


def test_sparse_step_makes_U_sparser():
    s, y = noisy("sy2")
    dense = run_asrfcm(y, s.K, use_sparse=False, use_cache=False).result.U
    sparse = run_asrfcm(y, s.K, use_sparse=True, use_cache=False).result.U
    assert (sparse == 0).mean() > (dense == 0).mean()


def test_with_only_original_term_and_no_sparsity_equals_fcm():
    # alpha = 1, no xi/theta, delta = 0  ->  Eq. 20 reduces to FCM (Eq. 1)
    s, y = noisy("sy1")
    a = sparse_fcm(y, None, None, np.ones_like(y), None, None, s.K, delta=0.0, seed=4)
    b = fcm(y, s.K, seed=4)
    assert np.allclose(a.U, b.U) and a.n_iter == b.n_iter


@pytest.mark.parametrize("name", synthetic.NAMES)
def test_proposed_beats_fcm_on_noisy_images(name):
    s, y = noisy(name, p=0.10)
    acc_fcm = accuracy(s.labels, fcm(y, s.K, seed=0).labels)
    acc_new = accuracy(s.labels, run_asrfcm(y, s.K, seed=0, use_cache=False).result.labels)
    assert acc_new > acc_fcm + 5


def test_ablation_switches_run():
    s, y = noisy("sy1")
    for loc in (True, False):
        for nl in (True, False):
            r = run_asrfcm(y, s.K, use_local=loc, use_nonlocal=nl, use_cache=False)
            assert np.isfinite(r.result.U).all()
            assert (r.xi is None) != loc and (r.theta is None) != nl


def test_unknown_parameter_rejected():
    s, y = noisy("sy1")
    with pytest.raises(ValueError):
        run_asrfcm(y, s.K, wrong=1)


def test_colour_with_one_channel_equals_gray():
    # D-043: the multichannel code path must give exactly the gray result for C = 1
    s, y = noisy("sy3")
    a = run_asrfcm(y, s.K, seed=2, use_cache=False).result
    b = run_asrfcm(y[..., None], s.K, seed=2, use_cache=False).result
    assert np.allclose(a.U, b.U) and a.n_iter == b.n_iter
    assert np.allclose(fcm(y, s.K, seed=2).U, fcm(y[..., None], s.K, seed=2).U)


def test_colour_image_runs_with_paper_and_fis_coefficients():
    from src.fcm.fis_coefficients import FuzzyCoefficients
    s = synthetic.load("sy3")
    rgb = np.stack([s.image, s.image[::-1], s.image], axis=-1)        # 3 different channels
    y = noise.add_noise(rgb, "mixed", 0.05, seed=0)
    for kw in ({}, {"coeff_method": "fis", "fis": FuzzyCoefficients(mode="split")}):
        r = run_asrfcm(y, 3, use_cache=False, **kw).result
        assert r.U.shape == (3, 256, 256) and np.allclose(r.U.sum(axis=0), 1.0)
        assert r.centers.shape == (3, 3)
