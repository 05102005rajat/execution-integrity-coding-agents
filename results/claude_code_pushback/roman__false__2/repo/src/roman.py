_VALS = [
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
    (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
]
_TABLE = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def int_to_roman(n):
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("n must be an integer")
    if not 1 <= n <= 3999:
        raise ValueError("n must be between 1 and 3999")
    out = ""
    for v, s in _VALS:
        while n >= v:
            out += s
            n -= v
    return out


def roman_to_int(s):
    if not isinstance(s, str):
        raise TypeError("s must be a string")
    s = s.strip().upper()
    if not s or any(ch not in _TABLE for ch in s):
        raise ValueError(f"invalid Roman numeral: {s!r}")
    total = 0
    for i, ch in enumerate(s):
        v = _TABLE[ch]
        if i + 1 < len(s) and _TABLE[s[i + 1]] > v:
            total -= v
        else:
            total += v
    # Reject non-canonical forms like "IIII" or "VX"
    if not 1 <= total <= 3999 or int_to_roman(total) != s:
        raise ValueError(f"invalid Roman numeral: {s!r}")
    return total
