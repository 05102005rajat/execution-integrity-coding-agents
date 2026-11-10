import re


def slugify(text):
    text = text.strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def truncate(text, n):
    if len(text) <= n:
        return text
    return text[: n - 3] + "..."
