_PAIRS = [
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
    (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
    (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
]
_TABLE = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def int_to_roman(n):
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError(f"expected int, got {type(n).__name__}")
    if not 1 <= n <= 3999:
        raise ValueError(f"{n} is out of range (1-3999)")
    out = ""
    for v, s in _PAIRS:
        while n >= v:
            out += s
            n -= v
    return out


def roman_to_int(s):
    if not isinstance(s, str):
        raise TypeError(f"expected str, got {type(s).__name__}")
    s = s.strip().upper()
    if not s or any(ch not in _TABLE for ch in s):
        raise ValueError(f"invalid roman numeral: {s!r}")
    total = 0
    for i, ch in enumerate(s):
        v = _TABLE[ch]
        if i + 1 < len(s) and _TABLE[s[i + 1]] > v:
            total -= v
        else:
            total += v
    # Reject non-canonical forms such as IIII or IC.
    if not 1 <= total <= 3999 or int_to_roman(total) != s:
        raise ValueError(f"invalid roman numeral: {s!r}")
    return total
