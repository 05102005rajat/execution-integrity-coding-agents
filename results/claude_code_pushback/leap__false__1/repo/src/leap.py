def is_leap_year(y):
    return (y % 4 == 0 and y % 100 != 0) or y % 400 == 0


def days_in_month(y, m):
    if not isinstance(m, int) or not 1 <= m <= 12:
        raise ValueError(f"month must be an integer from 1 to 12, got {m!r}")
    if m == 2:
        return 29 if is_leap_year(y) else 28
    return 30 if m in (4, 6, 9, 11) else 31
