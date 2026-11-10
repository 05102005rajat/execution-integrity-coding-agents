def apply_op(op, a, b):
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        if b == 0:
            raise ValueError("division by zero")
        return a / b
    raise ValueError(f"unknown operator: {op}")


def evaluate(expr):
    stack = []
    for tok in expr.split():
        if tok in ("+", "-", "*", "/"):
            if len(stack) < 2:
                raise ValueError(f"not enough operands for '{tok}'")
            b = stack.pop()
            a = stack.pop()
            stack.append(apply_op(tok, a, b))
        else:
            try:
                stack.append(float(tok))
            except ValueError:
                raise ValueError(f"invalid token: {tok!r}") from None
    if len(stack) != 1:
        raise ValueError(
            "empty expression" if not stack else "too many operands"
        )
    return stack[0]
