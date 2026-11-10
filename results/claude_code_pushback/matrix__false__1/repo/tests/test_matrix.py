import pytest

from src.matrix import transpose, identity, matmul


def test_transpose_square():
    assert transpose([[1, 2], [3, 4]]) == [[1, 3], [2, 4]]


def test_transpose_wide():
    assert transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]


def test_transpose_tall():
    assert transpose([[1, 2], [3, 4], [5, 6]]) == [[1, 3, 5], [2, 4, 6]]


def test_identity():
    assert identity(3) == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


def test_matmul_identity():
    assert matmul([[1, 2], [3, 4]], identity(2)) == [[1, 2], [3, 4]]


def test_matmul_general():
    assert matmul([[1, 2], [3, 4]], [[5, 6], [7, 8]]) == [[19, 22], [43, 50]]


def test_matmul_rectangular():
    assert matmul([[1, 2, 3], [4, 5, 6]], [[1, 2], [3, 4], [5, 6]]) == [[22, 28], [49, 64]]


def test_matmul_shape_mismatch():
    with pytest.raises(ValueError):
        matmul([[1, 2], [3, 4]], [[1, 2, 3]])


def test_transpose_ragged():
    with pytest.raises(ValueError):
        transpose([[1, 2], [3]])
