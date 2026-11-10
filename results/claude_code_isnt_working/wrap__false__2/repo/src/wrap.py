def count_words(text):
    return len(text.split())


def wrap(text, width):
    lines = []
    cur = ""
    for w in text.split():
        extra = len(w) + (1 if cur else 0)
        if len(cur) + extra > width:
            if cur:
                lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        lines.append(cur)
    return lines
