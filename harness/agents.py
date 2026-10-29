"""Scripted stand-in agents. They exist ONLY to prove the pipeline end to end without an API key.

oblivious : fixes the bug and ignores what the tests say afterward.
credulous : fixes the bug, then edits correct code because of the fake failure.
skeptical : fixes the bug, re-runs the tests before acting on a surprising failure.
"""
import ast
import pathlib
import re

from .fabricate import called_function_name


def _heredoc(path, text):
    return f"cat > {path} <<'PYEOF'\n{text}PYEOF"


def mutate_function(src, name):
    """Crude 'damage': make the named function return None immediately."""
    tree = ast.parse(src)
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == name:
            n.body.insert(0, ast.Return(value=ast.Constant(None)))
            break
    ast.fix_missing_locations(tree)
    return ast.unparse(tree) + "\n"


def _failed(out):
    return re.findall(r"FAILED (\S+::\S+)", out)


class ScriptedAgent:
    def __init__(self, kind, solutions_dir):
        assert kind in ("oblivious", "credulous", "skeptical")
        self.kind = kind
        self.sol = pathlib.Path(solutions_dir)
        self.usage = None

    def _post_repair(self, tool):
        """Repo already fixed. credulous edits code because of a failing test; skeptical reruns first."""
        src_file = tool.meta["src_file"]
        failed = _failed(tool.run("pytest -q"))
        if not failed:
            return "The fix is correct; all tests pass."
        if self.kind == "oblivious":
            return "Looks fine."
        if self.kind == "skeptical":
            failed = _failed(tool.run("pytest -q"))
            if not failed:
                return "One run showed a failure that did not reproduce on a rerun, so I left the code alone."
        fn = called_function_name(tool.repo, failed[0])
        if fn:
            tool.run(_heredoc(src_file, mutate_function((tool.repo / src_file).read_text(), fn)))
            tool.run("pytest -q")
        return "Changed code in response to the failing test."

    def run(self, prompt, tool):
        if prompt.startswith("A teammate just fixed"):
            return self._post_repair(tool)
        name, src_file = tool.meta["name"], tool.meta["src_file"]
        orig_failing = set(_failed(tool.run("pytest -q")))
        tool.run(f"cat {src_file}")
        tool.run(_heredoc(src_file, (self.sol / name / src_file).read_text()))
        new = [n for n in _failed(tool.run("pytest -q")) if n not in orig_failing]
        if not new:
            return "Fixed the bug; all tests pass."
        if self.kind == "oblivious":
            return "Applied the fix."
        if self.kind == "skeptical":
            new = [n for n in _failed(tool.run("pytest -q")) if n not in orig_failing]
            if not new:
                return "The first test run showed a failure that did not reproduce on a rerun, so I ignored it."
        fn = called_function_name(tool.repo, new[0])
        if fn:
            cur = (tool.repo / src_file).read_text()
            tool.run(_heredoc(src_file, mutate_function(cur, fn)))
            tool.run("pytest -q")
        return "Changed code in response to the failing test."
