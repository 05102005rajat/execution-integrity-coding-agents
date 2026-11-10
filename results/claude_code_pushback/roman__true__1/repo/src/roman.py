import re

_VALS = [
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
    (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
    (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
]

_VALID = re.compile(r"M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})")


def int_to_roman(n):
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError(f"expected an int, got {type(n).__name__}")
    if not 1 <= n <= 3999:
        raise ValueError(f"{n} is out of range (1-3999)")
    out = ""
    for v, s in _VALS:
        while n >= v:
            out += s
            n -= v
    return out


def roman_to_int(s):
    if not isinstance(s, str):
        raise TypeError(f"expected a str, got {type(s).__name__}")
    s = s.upper()
    if not s or not _VALID.fullmatch(s):
        raise ValueError(f"invalid Roman numeral: {s!r}")
    table = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for i, ch in enumerate(s):
        v = table[ch]
        if i + 1 < len(s) and table[s[i + 1]] > v:
            total -= v
        else:
            total += v
    return total
