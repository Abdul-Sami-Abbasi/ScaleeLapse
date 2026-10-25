import pytest
from scripts.evaluation.evaluate import sus, iou, classification


def test_sus_and_iou():
    assert sus([5, 1] * 5) == 100
    assert sus([1, 5] * 5) == 0
    with pytest.raises(ValueError):
        sus([6] * 10)
    assert iou([0, 0, 10, 10], [0, 0, 10, 10]) == 1
    assert iou([0, 0, 10, 10], [20, 20, 30, 30]) == 0


def test_classification():
    r = classification([0, 1, 1, 0], [0, 1, 0, 0])
    assert r["accuracy"] == 0.75
