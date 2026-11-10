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


@pytest.mark.parametrize("bad", [0, -1, 4000])
def test_int_to_roman_out_of_range(bad):
    with pytest.raises(ValueError):
        int_to_roman(bad)


def test_int_to_roman_bad_type():
    with pytest.raises(TypeError):
        int_to_roman(3.5)


@pytest.mark.parametrize("bad", ["", "abc", "IIII", "VX", "IC"])
def test_roman_to_int_invalid(bad):
    with pytest.raises(ValueError):
        roman_to_int(bad)


def test_roman_to_int_lowercase():
    assert roman_to_int("iv") == 4


def test_round_trip():
    for n in range(1, 4000):
        assert roman_to_int(int_to_roman(n)) == n
