"""Checks every task: buggy repo has >=1 failing and >=3 passing tests, the reference fix passes everything."""
import json
import pathlib
import shutil
import sys
import tempfile

from harness.fabricate import statuses

ROOT = pathlib.Path(__file__).parent
ok = True
for t in sorted(p for p in (ROOT / "tasks").iterdir() if p.is_dir()):
    meta = json.loads((t / "task.json").read_text())
    with tempfile.TemporaryDirectory() as d:
        repo = pathlib.Path(d) / "r"
        shutil.copytree(t, repo, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        before = statuses(repo)
        sol = ROOT / "solutions" / meta["name"] / meta["src_file"]
        shutil.copy(sol, repo / meta["src_file"])
        after = statuses(repo)
    n_fail = sum(s != "PASSED" for s in before.values())
    n_pass = sum(s == "PASSED" for s in before.values())
    good = n_fail >= 1 and n_pass >= 3 and after and all(s == "PASSED" for s in after.values())
    ok &= bool(good)
    print(f"{'OK ' if good else 'BAD'} {meta['name']:12s} buggy: {n_fail} failing / {n_pass} passing; after fix: "
          f"{sum(s == 'PASSED' for s in after.values())}/{len(after)} pass")
sys.exit(0 if ok else 1)
