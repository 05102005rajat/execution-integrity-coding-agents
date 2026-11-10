_VALS = [
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
    (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
]


def int_to_roman(n):
    if isinstance(n, bool) or not isinstance(n, int):
        raise ValueError(f"expected an integer, got {n!r}")
    if not 1 <= n <= 3999:
        raise ValueError(f"number out of range (1-3999): {n}")
    out = ""
    for v, s in _VALS:
        while n >= v:
            out += s
            n -= v
    return out


def roman_to_int(s):
    if not isinstance(s, str) or not s:
        raise ValueError(f"expected a non-empty string, got {s!r}")
    table = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    s = s.upper()
    if any(ch not in table for ch in s):
        raise ValueError(f"invalid Roman numeral: {s!r}")
    total = 0
    for i, ch in enumerate(s):
        v = table[ch]
        if i + 1 < len(s) and table[s[i + 1]] > v:
            total -= v
        else:
            total += v
    # Reject non-canonical forms such as "IIII" or "IC".
    if int_to_roman(total) != s if 1 <= total <= 3999 else True:
        raise ValueError(f"invalid Roman numeral: {s!r}")
    return total
