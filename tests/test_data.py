import numpy as np
import pytest

from src.data import bsds500, synthetic


@pytest.mark.parametrize("name,K", [("sy1", 2), ("sy2", 3), ("sy3", 3)])
def test_synthetic_images(name, K):
    s = synthetic.load(name)
    assert s.K == K
    assert s.image.shape == s.labels.shape == (256, 256)
    assert set(np.unique(s.labels)) == set(range(K))  # every class present
    # piecewise constant: each class has exactly one gray value
    for k in range(K):
        assert np.unique(s.image[s.labels == k]).size == 1
    assert 0.0 <= s.image.min() and s.image.max() <= 1.0


def test_unknown_synthetic_name():
    with pytest.raises(ValueError):
        synthetic.load("sy4")


@pytest.mark.skipif(not bsds500.ROOT.exists(), reason="BSDS500 not downloaded (see data/README.md)")
def test_bsds_paper_images():
    for pid in bsds500.PAPER_IDS:
        im = bsds500.load(pid)
        assert im.gray.shape == im.rgb.shape[:2]
        assert 0.0 <= im.gray.min() and im.gray.max() <= 1.0
        assert len(im.ground_truths) >= 5
        gt = bsds500.select_ground_truth(im, "fewest")
        assert gt.min() == 0 and gt.shape == im.gray.shape
