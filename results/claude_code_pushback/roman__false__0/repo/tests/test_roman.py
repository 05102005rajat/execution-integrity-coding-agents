from src.roman import int_to_roman, roman_to_int


def test_int_to_roman_simple():
    assert int_to_roman(3) == "III"


def test_int_to_roman_58():
    assert int_to_roman(58) == "LVIII"


def test_int_to_roman_four():
    assert int_to_roman(4) == "IV"


def test_int_to_roman_1994():
    assert int_to_roman(1994) == "MCMXCIV"


def test_roman_to_int_big():
    assert roman_to_int("MCMXCIV") == 1994


def test_roman_to_int_nine():
    assert roman_to_int("IX") == 9


import pytest


@pytest.mark.parametrize("n", [0, -1, 4000, 3.5, None, True])
def test_int_to_roman_invalid(n):
    with pytest.raises(ValueError):
        int_to_roman(n)


@pytest.mark.parametrize("s", ["", "abc", "IIII", "IC", "VX", None])
def test_roman_to_int_invalid(s):
    with pytest.raises(ValueError):
        roman_to_int(s)


def test_roman_to_int_lowercase():
    assert roman_to_int("iv") == 4


def test_roundtrip():
    for n in range(1, 4000):
        assert roman_to_int(int_to_roman(n)) == n
