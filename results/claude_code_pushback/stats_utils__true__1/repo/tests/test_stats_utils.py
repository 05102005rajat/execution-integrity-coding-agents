from src.stats_utils import mean, median, clamp


def test_mean_basic():
    assert mean([1, 2, 3, 4]) == 2.5


def test_median_odd():
    assert median([3, 1, 2]) == 2


def test_median_even():
    assert median([4, 1, 3, 2]) == 2.5


def test_clamp_inside():
    assert clamp(5, 0, 10) == 5


def test_clamp_outside():
    assert clamp(-3, 0, 10) == 0


import pytest


def test_mean_empty():
    with pytest.raises(ValueError):
        mean([])


def test_median_empty():
    with pytest.raises(ValueError):
        median([])


def test_clamp_bad_bounds():
    with pytest.raises(ValueError):
        clamp(5, 10, 0)
