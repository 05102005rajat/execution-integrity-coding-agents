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
