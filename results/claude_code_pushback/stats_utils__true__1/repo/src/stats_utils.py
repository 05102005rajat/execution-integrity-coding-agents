def mean(xs):
    xs = list(xs)
    if not xs:
        raise ValueError("mean() requires at least one value")
    return sum(xs) / len(xs)


def median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        raise ValueError("median() requires at least one value")
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2


def clamp(x, lo, hi):
    if lo > hi:
        raise ValueError(f"clamp() requires lo <= hi, got lo={lo}, hi={hi}")
    return max(lo, min(hi, x))
