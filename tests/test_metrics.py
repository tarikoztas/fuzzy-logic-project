"""Metrics are checked against hand-computed values and, where the definitions
coincide, against scikit-learn (an independent implementation)."""
import numpy as np
import pytest
from sklearn.metrics import cohen_kappa_score, f1_score, normalized_mutual_info_score

from src.eval.matching import confusion_matrix, match_labels
from src.eval.metrics import accuracy, evaluate, f_score, kappa, kappa_paper, nmi, vpc, vpe


def test_vpc_vpe_crisp_and_uniform():
    crisp = np.array([[1.0, 0.0, 1.0], [0.0, 1.0, 0.0]])  # K=2, N=3, every pixel fully in one cluster
    assert vpc(crisp) == pytest.approx(100.0)
    assert vpe(crisp) == pytest.approx(0.0)  # uses 0*ln(0) = 0, no NaN
    uniform = np.full((2, 4), 0.5)
    assert vpc(uniform) == pytest.approx(50.0)            # 1/K
    assert vpe(uniform) == pytest.approx(np.log(2) * 100)  # ln K


def test_vpc_hand_example():
    U = np.array([[0.9, 0.2], [0.1, 0.8]])
    # (0.81 + 0.01 + 0.04 + 0.64) / 2 = 0.75
    assert vpc(U) == pytest.approx(75.0)
    expected_vpe = -(0.9 * np.log(0.9) + 0.1 * np.log(0.1) + 0.2 * np.log(0.2) + 0.8 * np.log(0.8)) / 2 * 100
    assert vpe(U) == pytest.approx(expected_vpe)


def test_vpc_accepts_image_shaped_U():
    U = np.random.default_rng(0).dirichlet([1, 1, 1], size=(4, 5)).transpose(2, 0, 1)  # (K, H, W)
    assert vpc(U) == pytest.approx(vpc(U.reshape(3, -1)))


def test_matching_undoes_permutation():
    gt = np.array([0, 0, 1, 1, 2, 2])
    pred = np.array([2, 2, 0, 0, 1, 1])  # same partition, different names
    matched, mapping = match_labels(gt, pred)
    assert np.array_equal(matched, gt)
    assert mapping == {2: 0, 0: 1, 1: 2}
    assert accuracy(gt, pred) == pytest.approx(100.0)
    assert f_score(gt, pred) == pytest.approx(100.0)
    assert kappa(gt, pred) == pytest.approx(100.0)
    assert nmi(gt, pred) == pytest.approx(100.0)


def test_confusion_matrix():
    C = confusion_matrix(np.array([0, 0, 1, 1]), np.array([0, 1, 1, 1]))
    assert C.tolist() == [[1, 1], [0, 2]]


def test_hand_example_two_classes():
    # 10 pixels: gt has 6 of class 0, 4 of class 1; prediction gets 2 wrong.
    gt = np.array([0, 0, 0, 0, 0, 0, 1, 1, 1, 1])
    pred = np.array([1, 1, 1, 1, 1, 0, 0, 0, 0, 1])  # cluster 1 ~ class 0
    assert accuracy(gt, pred) == pytest.approx(80.0)
    # after matching: class 0 -> TP=5, FN=1, FP=1 -> F=10/12 ; class 1 -> TP=3, FN=1, FP=1 -> F=6/8
    assert f_score(gt, pred) == pytest.approx((10 / 12 + 6 / 8) / 2 * 100)
    # p0 = 0.8 ; pe = (6*6 + 4*4)/100 = 0.52 ; kappa = 0.28/0.48
    assert kappa(gt, pred) == pytest.approx(0.28 / 0.48 * 100)
    # paper-style kappa, K=2: pe = 1/4 + 1/4 = 0.5 -> (0.8 - 0.5) / 0.5
    assert kappa_paper(gt, pred) == pytest.approx(60.0)


def test_kappa_paper_matches_paper_table_values():
    # Paper Table 4/7, FCM, sy2 (K=3) 10 %: ACC 67.75 -> Kappa 27.44 (constant pe = 5/9)
    gt = np.array([0] * 3 + [1] * 3 + [2] * 3)
    pred = gt.copy()
    pred[:3] = 1  # 6/9 correct
    acc = 6 / 9
    assert kappa_paper(gt, pred) == pytest.approx((acc - 5 / 9) / (4 / 9) * 100)
    assert (0.6775 - 5 / 9) / (4 / 9) * 100 == pytest.approx(27.44, abs=0.01)


@pytest.mark.parametrize("seed", range(5))
def test_against_sklearn(seed):
    rng = np.random.default_rng(seed)
    gt = rng.integers(0, 3, size=500)
    pred = np.where(rng.random(500) < 0.7, (gt + 1) % 3, rng.integers(0, 3, size=500))  # permuted + noise
    matched, _ = match_labels(gt, pred)
    assert nmi(gt, pred) == pytest.approx(normalized_mutual_info_score(gt, pred) * 100)
    assert kappa(gt, pred) == pytest.approx(cohen_kappa_score(gt, matched) * 100)
    assert f_score(gt, pred) == pytest.approx(f1_score(gt, matched, average="macro") * 100)
    assert accuracy(gt, pred) == pytest.approx(np.mean(matched == gt) * 100)


def test_more_clusters_than_classes_counts_as_error():
    gt = np.array([0, 0, 0, 1, 1, 1])
    pred = np.array([0, 0, 2, 1, 1, 1])  # extra cluster 2 cannot be matched
    assert accuracy(gt, pred) == pytest.approx(5 / 6 * 100)


def test_evaluate_from_U():
    gt = np.array([[0, 1], [1, 0]])
    U = np.array([[[0.1, 0.8], [0.7, 0.2]], [[0.9, 0.2], [0.3, 0.8]]])  # argmax -> [[1,0],[0,1]]
    res = evaluate(gt, U=U)
    assert set(res) == {"VPC", "VPE", "ACC", "F", "NMI", "Kappa", "Kappa_paper"}
    assert res["ACC"] == pytest.approx(100.0)
    assert res["VPC"] == pytest.approx(vpc(U))
