def transpose(m):
    rows = len(m)
    cols = len(m[0]) if m else 0
    return [[m[j][i] for j in range(rows)] for i in range(cols)]


def identity(n):
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def matmul(a, b):
    if a and b and len(a[0]) != len(b):
        raise ValueError(
            f"shape mismatch: {len(a)}x{len(a[0])} cannot multiply {len(b)}x{len(b[0])}"
        )
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]
