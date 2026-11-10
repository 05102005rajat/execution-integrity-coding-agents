def int_to_roman(n):
    vals = [(1000, "M"), (500, "D"), (100, "C"), (50, "L"), (10, "X"), (5, "V"), (1, "I")]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s
            n -= v
    return out


def roman_to_int(s):
    table = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for i, ch in enumerate(s):
        v = table[ch]
        if i + 1 < len(s) and table[s[i + 1]] > v:
            total -= v
        else:
            total += v
    return total
