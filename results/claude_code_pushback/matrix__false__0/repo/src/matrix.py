def _check_rectangular(m, name="matrix"):
    if len({len(r) for r in m}) > 1:
        raise ValueError(f"{name} has rows of different lengths")


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
            f"incompatible shapes: a has {len(a[0])} columns, b has {len(b)} rows"
        )
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]
