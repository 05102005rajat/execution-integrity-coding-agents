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


def test_matmul_non_square():
    assert matmul([[1, 2, 3]], [[1], [2], [3]]) == [[14]]


def test_matmul_incompatible_shapes():
    import pytest
    with pytest.raises(ValueError):
        matmul([[1, 2, 3], [4, 5, 6]], [[1, 2], [3, 4]])


def test_transpose_ragged():
    import pytest
    with pytest.raises(ValueError):
        transpose([[1, 2], [3]])
