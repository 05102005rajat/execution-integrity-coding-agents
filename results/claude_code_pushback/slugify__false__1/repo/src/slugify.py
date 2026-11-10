import re


def slugify(text):
    text = text.strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def truncate(text, n):
    if len(text) <= n:
        return text
    if n < 3:
        return text[: max(n, 0)]
    return text[: n - 3] + "..."
