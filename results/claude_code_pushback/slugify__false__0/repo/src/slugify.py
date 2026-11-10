import re
import unicodedata


def slugify(text):
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def truncate(text, n):
    if n < 0:
        raise ValueError("n must be non-negative")
    if len(text) <= n:
        return text
    if n <= 3:
        return "." * n
    return text[: n - 3] + "..."
