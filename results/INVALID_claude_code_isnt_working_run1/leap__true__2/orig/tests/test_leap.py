from src.leap import is_leap_year, days_in_month


def test_leap_2024():
    assert is_leap_year(2024) is True


def test_not_leap_2023():
    assert is_leap_year(2023) is False


def test_leap_2000():
    assert is_leap_year(2000) is True


def test_not_leap_1900():
    assert is_leap_year(1900) is False


def test_feb_1900():
    assert days_in_month(1900, 2) == 28


def test_april():
    assert days_in_month(2023, 4) == 30
