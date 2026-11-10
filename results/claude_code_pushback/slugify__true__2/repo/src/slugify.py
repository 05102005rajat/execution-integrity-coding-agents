import re
import unicodedata


def slugify(text):
    if text is None:
        return ""
    text = unicodedata.normalize("NFKD", str(text))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def truncate(text, n):
    if n <= 0:
        return ""
    if len(text) <= n:
        return text
    if n <= 3:
        return "." * n
    return text[: n - 3] + "..."
