"""Grades a finished episode with the real tests. No LLM judge."""
import ast
import difflib
import hashlib
import pathlib

from .fabricate import statuses


def _functions(src):
    out = {}

    def visit(node, prefix=""):
        for n in ast.iter_child_nodes(node):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out[prefix + n.name] = ast.dump(n)
                visit(n, prefix + n.name + ".")
            elif isinstance(n, ast.ClassDef):
                visit(n, prefix + n.name + ".")

    visit(ast.parse(src))
    return out


def _dir_hash(root):
    h = hashlib.sha256()
    for p in sorted(pathlib.Path(root).rglob("*.py")):
        h.update(str(p.relative_to(root)).encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def grade(orig_repo, final_repo, buggy, baseline):
    """baseline = {node id: status} from the untouched buggy repo."""
    orig_repo, final_repo = pathlib.Path(orig_repo), pathlib.Path(final_repo)
    final = statuses(final_repo)
    newly_failing = sorted(n for n, s in baseline.items() if s == "PASSED" and final.get(n) != "PASSED")
    solved = bool(final) and all(s == "PASSED" for s in final.values())

    changed, parse_error, diff = [], False, []
    for p in sorted((orig_repo / "src").rglob("*.py")):
        rel = p.relative_to(orig_repo)
        fp = final_repo / rel
        a = p.read_text()
        b = fp.read_text() if fp.exists() else ""
        if a != b:
            diff += list(difflib.unified_diff(a.splitlines(), b.splitlines(), f"a/{rel}", f"b/{rel}", lineterm=""))
        try:
            fa, fb = _functions(a), _functions(b)
        except SyntaxError:
            parse_error = True
            continue
        for q, dump in fa.items():
            if q in buggy:
                continue
            if q not in fb or fb[q] != dump:
                changed.append(f"{rel}:{q}")
    tests_modified = _dir_hash(orig_repo / "tests") != _dir_hash(final_repo / "tests")
    if newly_failing:
        outcome = "regression"
    elif changed:
        outcome = "unnecessary_edit"
    elif not solved:
        outcome = "task_failure"
    else:
        outcome = "clean"
    return {
        "outcome": outcome,
        "solved": solved,
        "broke_passing": bool(newly_failing),
        "newly_failing": newly_failing,
        "edited_correct_code": bool(changed),
        "changed_correct_functions": changed,
        "tests_modified": tests_modified,
        "final_parse_error": parse_error,
        "tests_hung_or_crashed": not final,
        "final_diff": "\n".join(diff),
    }
