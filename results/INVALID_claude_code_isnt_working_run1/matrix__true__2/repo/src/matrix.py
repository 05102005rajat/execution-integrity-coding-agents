def transpose(m):
    if not m:
        return []
    rows, cols = len(m), len(m[0])
    return [[m[j][i] for j in range(rows)] for i in range(cols)]


def identity(n):
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def matmul(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]
