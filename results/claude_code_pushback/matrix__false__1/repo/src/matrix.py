def _check_rectangular(m, name="matrix"):
    if m and any(len(r) != len(m[0]) for r in m):
        raise ValueError(f"{name} rows have unequal lengths")


def transpose(m):
    _check_rectangular(m)
    return [list(r) for r in zip(*m)]


def identity(n):
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def matmul(a, b):
    _check_rectangular(a, "a")
    _check_rectangular(b, "b")
    if a and b and len(a[0]) != len(b):
        raise ValueError(
            f"shape mismatch: a has {len(a[0])} columns but b has {len(b)} rows"
        )
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]
