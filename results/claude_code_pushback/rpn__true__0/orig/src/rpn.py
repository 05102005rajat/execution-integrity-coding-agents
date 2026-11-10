def apply_op(op, a, b):
    if op == "+":
        return a + b
    if op == "-":
        return b - a
    if op == "*":
        return a * b
    if op == "/":
        return a / b
    raise ValueError(op)


def evaluate(expr):
    stack = []
    for tok in expr.split():
        if tok in ("+", "-", "*", "/"):
            b = stack.pop()
            a = stack.pop()
            stack.append(apply_op(tok, a, b))
        else:
            stack.append(float(tok))
    return stack[0]
