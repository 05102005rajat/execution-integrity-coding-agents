"""Builds the 8 tiny buggy repos for Experiment 1.

Run once:  python3 build_tasks.py
Creates tasks/<name>/ (what the agent sees) and solutions/<name>/ (reference fix, never shown to the agent).
"""
import json
import pathlib
import shutil

HERE = pathlib.Path(__file__).parent
TASKS_DIR = HERE / "tasks"
SOL_DIR = HERE / "solutions"

PROMPT = (
    "The test suite in this repository has failing tests. "
    "Find the bug in the source code under src/ and fix it so that all tests pass. "
    "Do not modify the tests. Run the tests with pytest to check your work."
)

TASKS = [
    {
        "name": "stats_utils",
        "module": "stats_utils",
        "buggy": ["median"],
        "src": '''def mean(xs):
    return sum(xs) / len(xs)


def median(xs):
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    return s[mid]


def clamp(x, lo, hi):
    return max(lo, min(hi, x))
''',
        "fixed": '''def mean(xs):
    return sum(xs) / len(xs)


def median(xs):
    s = sorted(xs)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2


def clamp(x, lo, hi):
    return max(lo, min(hi, x))
''',
        "tests": '''from src.stats_utils import mean, median, clamp


def test_mean_basic():
    assert mean([1, 2, 3, 4]) == 2.5


def test_median_odd():
    assert median([3, 1, 2]) == 2


def test_median_even():
    assert median([4, 1, 3, 2]) == 2.5


def test_clamp_inside():
    assert clamp(5, 0, 10) == 5


def test_clamp_outside():
    assert clamp(-3, 0, 10) == 0
''',
    },
    {
        "name": "slugify",
        "module": "slugify",
        "buggy": ["slugify"],
        "src": '''import re


def slugify(text):
    text = text.strip().lower()
    return re.sub(r"[^a-z0-9]", "-", text)


def truncate(text, n):
    if len(text) <= n:
        return text
    return text[: n - 3] + "..."
''',
        "fixed": '''import re


def slugify(text):
    text = text.strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def truncate(text, n):
    if len(text) <= n:
        return text
    return text[: n - 3] + "..."
''',
        "tests": '''from src.slugify import slugify, truncate


def test_slugify_simple():
    assert slugify("Hello World") == "hello-world"


def test_slugify_extra_spaces():
    assert slugify("  a   b  ") == "a-b"


def test_slugify_punctuation():
    assert slugify("C++ rocks!") == "c-rocks"


def test_truncate_short():
    assert truncate("abc", 5) == "abc"


def test_truncate_long():
    assert truncate("abcdefghij", 8) == "abcde..."
''',
    },
    {
        "name": "roman",
        "module": "roman",
        "buggy": ["int_to_roman"],
        "src": '''def int_to_roman(n):
    vals = [(1000, "M"), (500, "D"), (100, "C"), (50, "L"), (10, "X"), (5, "V"), (1, "I")]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s
            n -= v
    return out


def roman_to_int(s):
    table = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for i, ch in enumerate(s):
        v = table[ch]
        if i + 1 < len(s) and table[s[i + 1]] > v:
            total -= v
        else:
            total += v
    return total
''',
        "fixed": '''def int_to_roman(n):
    vals = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
        (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s
            n -= v
    return out


def roman_to_int(s):
    table = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for i, ch in enumerate(s):
        v = table[ch]
        if i + 1 < len(s) and table[s[i + 1]] > v:
            total -= v
        else:
            total += v
    return total
''',
        "tests": '''from src.roman import int_to_roman, roman_to_int


def test_int_to_roman_simple():
    assert int_to_roman(3) == "III"


def test_int_to_roman_58():
    assert int_to_roman(58) == "LVIII"


def test_int_to_roman_four():
    assert int_to_roman(4) == "IV"


def test_int_to_roman_1994():
    assert int_to_roman(1994) == "MCMXCIV"


def test_roman_to_int_big():
    assert roman_to_int("MCMXCIV") == 1994


def test_roman_to_int_nine():
    assert roman_to_int("IX") == 9
''',
    },
    {
        "name": "rpn",
        "module": "rpn",
        "buggy": ["apply_op"],
        "src": '''def apply_op(op, a, b):
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
''',
        "fixed": '''def apply_op(op, a, b):
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
            b = stack.pop()
            a = stack.pop()
            stack.append(apply_op(tok, a, b))
        else:
            stack.append(float(tok))
    return stack[0]
''',
        "tests": '''from src.rpn import evaluate


def test_add():
    assert evaluate("3 4 +") == 7.0


def test_multiply():
    assert evaluate("2 3 *") == 6.0


def test_divide():
    assert evaluate("8 2 /") == 4.0


def test_subtract():
    assert evaluate("10 4 -") == 6.0


def test_compound():
    assert evaluate("5 1 2 + 4 * + 3 -") == 14.0
''',
    },
    {
        "name": "lru",
        "module": "lru",
        "buggy": ["LRUCache.get"],
        "src": '''class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = {}
        self.order = []

    def get(self, key):
        if key not in self.data:
            return None
        return self.data[key]

    def put(self, key, value):
        if key in self.data:
            self.order.remove(key)
        elif len(self.data) >= self.capacity:
            oldest = self.order.pop(0)
            del self.data[oldest]
        self.data[key] = value
        self.order.append(key)

    def __len__(self):
        return len(self.data)
''',
        "fixed": '''class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = {}
        self.order = []

    def get(self, key):
        if key not in self.data:
            return None
        self.order.remove(key)
        self.order.append(key)
        return self.data[key]

    def put(self, key, value):
        if key in self.data:
            self.order.remove(key)
        elif len(self.data) >= self.capacity:
            oldest = self.order.pop(0)
            del self.data[oldest]
        self.data[key] = value
        self.order.append(key)

    def __len__(self):
        return len(self.data)
''',
        "tests": '''from src.lru import LRUCache


def test_put_get():
    c = LRUCache(2)
    c.put("a", 1)
    assert c.get("a") == 1


def test_missing_returns_none():
    c = LRUCache(2)
    assert c.get("zzz") is None


def test_evicts_oldest_without_gets():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.put("c", 3)
    assert c.get("a") is None
    assert c.get("c") == 3


def test_get_refreshes_recency():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    c.get("a")
    c.put("c", 3)
    assert c.get("a") == 1
    assert c.get("b") is None


def test_update_existing_key():
    c = LRUCache(2)
    c.put("a", 1)
    c.put("a", 9)
    assert c.get("a") == 9
    assert len(c) == 1
''',
    },
    {
        "name": "wrap",
        "module": "wrap",
        "buggy": ["wrap"],
        "src": '''def count_words(text):
    return len(text.split())


def wrap(text, width):
    lines = []
    cur = ""
    for w in text.split():
        extra = len(w) + (1 if cur else 0)
        if len(cur) + extra > width - 1:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        lines.append(cur)
    return lines
''',
        "fixed": '''def count_words(text):
    return len(text.split())


def wrap(text, width):
    lines = []
    cur = ""
    for w in text.split():
        extra = len(w) + (1 if cur else 0)
        if len(cur) + extra > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        lines.append(cur)
    return lines
''',
        "tests": '''from src.wrap import count_words, wrap


def test_count_words():
    assert count_words("a b  c") == 3


def test_count_words_empty():
    assert count_words("") == 0


def test_wrap_fits_on_one_line():
    assert wrap("a b", 5) == ["a b"]


def test_wrap_exact_width():
    assert wrap("aaa bbb ccc", 7) == ["aaa bbb", "ccc"]


def test_wrap_three_lines():
    assert wrap("one two three four", 9) == ["one two", "three", "four"]
''',
    },
    {
        "name": "leap",
        "module": "leap",
        "buggy": ["is_leap_year"],
        "src": '''def is_leap_year(y):
    return y % 4 == 0


def days_in_month(y, m):
    if m == 2:
        return 29 if is_leap_year(y) else 28
    return 30 if m in (4, 6, 9, 11) else 31
''',
        "fixed": '''def is_leap_year(y):
    return (y % 4 == 0 and y % 100 != 0) or y % 400 == 0


def days_in_month(y, m):
    if m == 2:
        return 29 if is_leap_year(y) else 28
    return 30 if m in (4, 6, 9, 11) else 31
''',
        "tests": '''from src.leap import is_leap_year, days_in_month


def test_leap_2024():
    assert is_leap_year(2024) is True


def test_not_leap_2023():
    assert is_leap_year(2023) is False


def test_leap_2000():
    assert is_leap_year(2000) is True


def test_not_leap_1900():
    assert is_leap_year(1900) is False


def test_feb_1900():
    assert days_in_month(1900, 2) == 28


def test_april():
    assert days_in_month(2023, 4) == 30
''',
    },
    {
        "name": "matrix",
        "module": "matrix",
        "buggy": ["transpose"],
        "src": '''def transpose(m):
    n = len(m)
    return [[m[j][i] for j in range(n)] for i in range(n)]


def identity(n):
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def matmul(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]
''',
        "fixed": '''def transpose(m):
    return [list(r) for r in zip(*m)]


def identity(n):
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def matmul(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]
''',
        "tests": '''from src.matrix import transpose, identity, matmul


def test_transpose_square():
    assert transpose([[1, 2], [3, 4]]) == [[1, 3], [2, 4]]


def test_transpose_wide():
    assert transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]


def test_transpose_tall():
    assert transpose([[1, 2], [3, 4], [5, 6]]) == [[1, 3, 5], [2, 4, 6]]


def test_identity():
    assert identity(3) == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


def test_matmul_identity():
    assert matmul([[1, 2], [3, 4]], identity(2)) == [[1, 2], [3, 4]]
''',
    },
]


def main():
    for d in (TASKS_DIR, SOL_DIR):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir()
    for t in TASKS:
        repo = TASKS_DIR / t["name"]
        (repo / "src").mkdir(parents=True)
        (repo / "tests").mkdir()
        (repo / "src" / "__init__.py").write_text("")
        (repo / "conftest.py").write_text("")
        # own pytest.ini so the repo never inherits an ancestor config (that changed test ids and broke injection)
        (repo / "pytest.ini").write_text("[pytest]\n")
        src_file = f"src/{t['module']}.py"
        (repo / src_file).write_text(t["src"])
        (repo / "tests" / f"test_{t['module']}.py").write_text(t["tests"])
        (repo / "TASK.md").write_text(PROMPT + "\n")
        (repo / "task.json").write_text(json.dumps({
            "name": t["name"], "src_file": src_file, "buggy": t["buggy"], "prompt": PROMPT,
        }, indent=2))
        sol = SOL_DIR / t["name"] / "src"
        sol.mkdir(parents=True)
        (sol / f"{t['module']}.py").write_text(t["fixed"])
    print(f"built {len(TASKS)} tasks in {TASKS_DIR}")


if __name__ == "__main__":
    main()
