def transpose(m):
    return [list(r) for r in zip(*m)]


def identity(n):
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def matmul(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]
