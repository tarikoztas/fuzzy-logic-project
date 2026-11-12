import dtcwt
import numpy as np
import pytest

from src.data import noise, synthetic
from src.fcm.nonlocal_wavelet import gaussian_patch_kernel, nlm_subband, nonlocal_wavelet_info


def test_dtcwt_perfect_reconstruction():
    img = np.random.default_rng(0).random((64, 48)) * 255
    t = dtcwt.Transform2d()
    rec = t.inverse(t.forward(img, nlevels=1))
    assert np.abs(rec - img).max() < 1e-10


def test_kernel_normalised_and_symmetric():
    k = gaussian_patch_kernel(5, 4.0)
    assert k.shape == (5, 5) and k.sum() == pytest.approx(1.0)
    assert np.allclose(k, k.T) and k[2, 2] == k.max()


def test_constant_image_unchanged():
    img = np.full((32, 40), 0.3)
    assert np.allclose(nonlocal_wavelet_info(img), 0.3, atol=1e-10)


def test_odd_sizes_supported():
    img = np.random.default_rng(1).random((21, 33))
    assert nonlocal_wavelet_info(img, S=5, w=3).shape == (21, 33)


def slow_nlm(band, S, w, upsilon, g):
    """Direct transcription of Eqs. 10-11 (pixel loops) for a small real band."""
    s, r = S // 2, w // 2
    pad = s + r
    p = np.pad(band, pad, mode="symmetric")
    k = gaussian_patch_kernel(w, upsilon)
    out = np.zeros_like(band, dtype=float)
    H, W = band.shape
    for i in range(H):
        for j in range(W):
            ci, cj = i + pad, j + pad
            Pj = p[ci - r:ci + r + 1, cj - r:cj + r + 1]
            num = Z = 0.0
            for dy in range(-s, s + 1):
                for dx in range(-s, s + 1):
                    if dy == 0 and dx == 0:
                        continue
                    qi, qj = ci + dy, cj + dx
                    Pq = p[qi - r:qi + r + 1, qj - r:qj + r + 1]
                    wgt = np.exp(-np.sum(k * (Pq - Pj) ** 2) / (g * w * w))
                    num += wgt * p[qi, qj]
                    Z += wgt
            out[i, j] = num / Z
    return out


def test_vectorised_nlm_matches_equations():
    band = np.random.default_rng(2).random((9, 12)) * 60
    fast = nlm_subband(band, S=5, w=3, upsilon=4.0, g=10.0)
    assert np.allclose(fast, slow_nlm(band, 5, 3, 4.0, 10.0))


def test_complex_band_uses_magnitude_weights():
    rng = np.random.default_rng(3)
    band = rng.normal(size=(10, 10)) + 1j * rng.normal(size=(10, 10))
    out = nlm_subband(band, S=5, w=3)
    ref_re = nlm_subband_with_weights_from(np.abs(band), band.real)
    assert np.allclose(out.real, ref_re)


def nlm_subband_with_weights_from(mag, values, S=5, w=3, upsilon=4.0, g=10.0):
    # reference: weights computed from `mag`, applied to `values` (D-010)
    s, r = S // 2, w // 2
    pad = s + r
    mp = np.pad(mag, pad, mode="symmetric")
    vp = np.pad(values, pad, mode="symmetric")
    k = gaussian_patch_kernel(w, upsilon)
    H, W = mag.shape
    out = np.zeros((H, W))
    for i in range(H):
        for j in range(W):
            ci, cj = i + pad, j + pad
            Pj = mp[ci - r:ci + r + 1, cj - r:cj + r + 1]
            num = Z = 0.0
            for dy in range(-s, s + 1):
                for dx in range(-s, s + 1):
                    if dy == 0 and dx == 0:
                        continue
                    Pq = mp[ci + dy - r:ci + dy + r + 1, cj + dx - r:cj + dx + r + 1]
                    wgt = np.exp(-np.sum(k * (Pq - Pj) ** 2) / (g * w * w))
                    num += wgt * vp[ci + dy, cj + dx]
                    Z += wgt
            out[i, j] = num / Z
    return out


@pytest.mark.parametrize("name", synthetic.NAMES)
def test_theta_reduces_noise(name):
    s = synthetic.load(name)
    noisy = noise.add_noise(s.image, "mixed", 0.05, seed=0)
    theta = nonlocal_wavelet_info(noisy)
    assert np.abs(theta - s.image).mean() < np.abs(noisy - s.image).mean()
