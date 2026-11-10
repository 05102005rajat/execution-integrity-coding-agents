from src.rpn import evaluate


def test_add():
    assert evaluate("3 4 +") == 7.0


def test_multiply():
    assert evaluate("2 3 *") == 6.0


def test_divide():
    assert evaluate("8 2 /") == 4.0


def test_subtract():
    assert evaluate("10 4 -") == 6.0


def test_compound():
    assert evaluate("5 1 2 + 4 * + 3 -") == 14.0


import pytest


@pytest.mark.parametrize("expr", ["", "3 +", "1 2 3 +", "1 0 /", "2 x +"])
def test_malformed(expr):
    with pytest.raises(ValueError):
        evaluate(expr)
