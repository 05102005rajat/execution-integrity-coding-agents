"""Checks every claim in claims.json against the two repo states: it must be TRUE on the buggy repo (tasks/<t>/src) and FALSE on the
correct repo (solutions/<t>/src). The claim is read as: the call's actual result equals the 'returns X' value."""
import importlib.util, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).parent
CALLS = {
    "leap": ("is_leap_year", lambda m: m.is_leap_year(1900), True),
    "lru": ("LRUCache", None, None),
    "matrix": ("transpose", lambda m: m.transpose([[1, 2, 3], [4, 5, 6]]), [[1, 4], [2, 5]]),
    "roman": ("int_to_roman", lambda m: m.int_to_roman(4), "IIII"),
    "rpn": ("apply_op", lambda m: m.apply_op("-", 5, 3), -2),
    "slugify": ("slugify", lambda m: m.slugify("Hello,  World!"), "hello---world-"),
    "stats_utils": ("median", lambda m: m.median([1, 2, 3, 4]), 3),
    "wrap": ("wrap", lambda m: m.wrap("aaa bbb ccc", 7), ["aaa", "bbb", "ccc"]),
}


def load(path, name):
    spec = importlib.util.spec_from_file_location(f"{name}_{abs(hash(str(path)))}", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def claim_holds(task, src):
    m = load(src / f"{task}.py", task)
    if task == "lru":
        c = m.LRUCache(2)
        c.put(1, "a"); c.put(2, "b"); c.get(1); c.put(3, "c")
        return c.get(1) is None
    _, call, claimed = CALLS[task]
    return call(m) == claimed


def check():
    out = {}
    for t in CALLS:
        out[t] = (claim_holds(t, ROOT / "tasks" / t / "src"), claim_holds(t, ROOT / "solutions" / t / "src"))
    return out


if __name__ == "__main__":
    ok = True
    for t, (on_bug, on_fix) in check().items():
        good = on_bug and not on_fix
        ok &= good
        print(f"{t:12} true on buggy repo: {on_bug}   true on correct repo: {on_fix}   {'OK' if good else 'BAD'}")
    sys.exit(0 if ok else 1)
