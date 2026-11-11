"""Tests for the local spatial information xi (Algorithm 2), based on the
worked examples of the paper (Figs. 1-3) and on simple properties."""
import numpy as np
import pytest

from src.fcm.local_info import local_spatial_info, reward_mask, reward_size, similarity_weights

# 3x3 neighbour positions in raster order without the centre, and their distances
DIST8 = np.array([np.sqrt(2), 1, np.sqrt(2), 1, 1, np.sqrt(2), 1, np.sqrt(2)])


def neighbours(grid):
    g = np.asarray(grid, dtype=float)
    return g[1, 1], np.delete(g.ravel(), 4)


def test_reward_size_golden_ratio():
    assert reward_size(8) == 4            # Fig. 1: 0.618 * 8 = 4.94 -> 4 shown
    assert reward_size(8, rounding="ceil") == 5   # what the text's ceiling would give
    assert reward_size(24) == 14          # 5x5 window (w = 5)


def test_fig1_reward_and_penalty_sets():
    # Paper Fig. 1(b): 3x3 window, centre not used
    _, nb = neighbours([[137, 103, 194], [174, 0, 172], [169, 176, 212]])
    mask = reward_mask(nb)
    assert sorted(nb[mask]) == [169, 172, 174, 176]    # reward set in Fig. 1(c)
    assert sorted(nb[~mask]) == [103, 137, 194, 212]   # penalty set in Fig. 1(c)


def xi_window(grid, sigma=0.3):
    c, nb = neighbours(np.asarray(grid) / 255)
    ss = similarity_weights(np.array(c), nb, DIST8, sigma)
    return float((ss * nb).sum() / ss.sum() * 255)


def test_fig2_fig3_examples_follow_the_equations():
    # Paper Fig. 2 (centre 173, true 170) and Fig. 3 (centre 255 = noise, true 170).
    # Paper-reported xi: 166 and 175. Eqs. 5-9 as written (N_R = 9) give 167.9 and 197.7:
    # the similarity values printed in the figures do not follow Eqs. 5-6 (D-032).
    fig2 = [[145, 255, 254], [95, 173, 145], [21, 222, 151]]
    fig3 = [[200, 141, 132], [216, 255, 212], [147, 154, 211]]
    assert xi_window(fig2) == pytest.approx(167.9, abs=0.1)
    assert xi_window(fig3) == pytest.approx(197.7, abs=0.1)
    # both move the centre value towards the true value 170
    assert abs(xi_window(fig2) - 170) < abs(173 - 170)
    assert abs(xi_window(fig3) - 170) < abs(255 - 170)


def test_reward_pixels_get_more_weight_than_equal_penalty_pixels():
    c = np.array(0.5)
    nb = np.array([0.1, 0.2, 0.45, 0.5, 0.5, 0.55, 0.8, 0.9])
    ss = similarity_weights(c, nb, np.ones(8), sigma=0.3)
    mask = reward_mask(nb)
    assert ss[mask].min() > ss[~mask].max()


def test_constant_image_unchanged():
    img = np.full((20, 30), 0.4)
    assert np.allclose(local_spatial_info(img), 0.4)


def test_shape_range_and_window_check():
    img = np.random.default_rng(0).random((17, 23))
    xi = local_spatial_info(img, w=5)
    assert xi.shape == img.shape
    assert xi.min() >= img.min() - 1e-12 and xi.max() <= img.max() + 1e-12  # a weighted mean
    with pytest.raises(ValueError):
        local_spatial_info(img, w=4)


def test_matches_slow_reference_implementation():
    rng = np.random.default_rng(1)
    img = rng.random((9, 11))
    w, r = 5, 2
    fast = local_spatial_info(img, w=w)
    pad = np.pad(img, r, mode="symmetric")
    dy, dx = np.mgrid[-r:r + 1, -r:r + 1]
    dist = np.delete(np.hypot(dy, dx).ravel(), w * w // 2)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            nb = np.delete(pad[i:i + w, j:j + w].ravel(), w * w // 2)
            ss = similarity_weights(np.array(img[i, j]), nb, dist, 0.3)
            assert fast[i, j] == pytest.approx((ss * nb).sum() / ss.sum())


def test_salt_and_pepper_is_suppressed():
    img = np.full((15, 15), 0.6)
    img[7, 7] = 1.0          # salt at the centre
    img[6, 6] = 0.0          # pepper next to it
    xi = local_spatial_info(img, w=3)
    assert abs(xi[7, 7] - 0.6) < 0.05
