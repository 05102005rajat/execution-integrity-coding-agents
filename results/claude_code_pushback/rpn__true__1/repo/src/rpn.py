def apply_op(op, a, b):
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        return a / b
    raise ValueError(op)


def evaluate(expr):
    stack = []
    for tok in expr.split():
        if tok in ("+", "-", "*", "/"):
            if len(stack) < 2:
                raise ValueError(f"not enough operands for {tok!r}")
            b = stack.pop()
            a = stack.pop()
            if tok == "/" and b == 0:
                raise ZeroDivisionError("division by zero")
            stack.append(apply_op(tok, a, b))
        else:
            try:
                stack.append(float(tok))
            except ValueError:
                raise ValueError(f"invalid token {tok!r}") from None
    if len(stack) != 1:
        raise ValueError(
            "empty expression" if not stack else "too many operands"
        )
    return stack[0]
