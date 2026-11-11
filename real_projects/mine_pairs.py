#!/usr/bin/env python3
"""Mine (clean, bug) pairs from cloned pure-Python libraries (2026-11-10).

For each repo: look at recent commits whose message mentions fix/bug, that touch BOTH a source file and a test file, with a small diff.
Candidate variant dirs are built as:
  <out>/<name>-clean = repo at the fix commit (no .git)
  <out>/<name>-bug   = parent of the fix commit + the fix commit's version of the changed test files
A pair is KEPT only if, inside a no-network sandbox, the changed test files all PASS on clean and at least one FAILS on bug,
and the full test dir passes on clean. Nothing is run outside the sandbox. Usage:
  mine_pairs.py CLONES_DIR OUT_DIR PYTHON [max_per_repo]
"""
import pathlib, re, shutil, subprocess, sys, json

clones, out, py = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
max_per = int(sys.argv[4]) if len(sys.argv) > 4 else 1


def sh(*a, cwd=None, inp=None):
    return subprocess.run(a, cwd=cwd, capture_output=True, text=True, input=inp, timeout=600)


def sandboxed_pytest(d, paths):
    prof = ('(version 1)(allow default)(deny network*)(deny file-write*)(allow file-write* (subpath "%s") (subpath "/private/tmp") '
            '(subpath "/private/var/folders") (literal "/dev/null"))' % str(pathlib.Path(d).resolve()))
    return subprocess.run(["sandbox-exec", "-p", prof, "env", "PYTHONDONTWRITEBYTECODE=1", py, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", *paths],
                          cwd=d, capture_output=True, text=True, timeout=900)


def export(repo, rev, dest):
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True)
    a = subprocess.Popen(["git", "-C", str(repo), "archive", rev], stdout=subprocess.PIPE)
    subprocess.run(["tar", "x", "-C", str(dest)], stdin=a.stdout, check=True)
    a.wait()


kept = []
for repo in sorted(p for p in clones.iterdir() if (p / ".git").exists()):
    name = repo.name.replace("python-", "")
    log = sh("git", "log", "--since=2024-06-01", "--no-merges", "--format=%h %s", cwd=repo).stdout.splitlines()
    n = 0
    for line in log:
        h, subj = line.split(" ", 1)
        if not re.search(r"\b(fix|bug|crash|error|wrong|incorrect)", subj, re.I):
            continue
        files = sh("git", "show", "--numstat", "--format=", h, cwd=repo).stdout.strip().splitlines()
        rows = [f.split("\t") for f in files if f.count("\t") == 2]
        if not rows or any(r[0] == "-" for r in rows):
            continue
        tests = [r[2] for r in rows if re.search(r"(^|/)tests?(/|_)|test_", r[2]) and r[2].endswith(".py")]
        src = [r[2] for r in rows if r[2].endswith(".py") and r[2] not in tests and not r[2].startswith(("docs/", "doc/", "examples/"))]
        other = [r[2] for r in rows if r[2] not in tests and r[2] not in src and not r[2].endswith((".rst", ".md", ".txt", ".cfg", ".toml"))]
        if not tests or not src or other or len(src) > 2 or sum(int(r[0]) + int(r[1]) for r in rows if r[2] in src) > 40:
            continue
        cl, bg = out / f"{name}{n}-clean", out / f"{name}{n}-bug"
        try:
            export(repo, h, cl)
            export(repo, h + "^", bg)
            for t in tests:
                (bg / t).parent.mkdir(parents=True, exist_ok=True)
                (bg / t).write_text(sh("git", "show", f"{h}:{t}", cwd=repo).stdout)
            rc = sandboxed_pytest(cl, tests)
            rb = sandboxed_pytest(bg, tests)
            tdir = str(pathlib.Path(tests[0]).parts[0])
            full = sandboxed_pytest(cl, [tdir]) if (cl / tdir).is_dir() else rc
        except Exception as e:  # noqa
            print("skip", name, h, type(e).__name__)
            shutil.rmtree(cl, ignore_errors=True); shutil.rmtree(bg, ignore_errors=True)
            continue
        ok = rc.returncode == 0 and rb.returncode != 0 and full.returncode == 0
        print(("KEEP" if ok else "drop"), name, h, subj[:70], "| clean", rc.returncode, "bug", rb.returncode, "full", full.returncode)
        if ok:
            kept.append({"name": f"{name}{n}", "repo": repo.name, "commit": h, "subject": subj, "src": src, "tests": tests, "tests_dir": tdir})
            n += 1
        else:
            shutil.rmtree(cl, ignore_errors=True); shutil.rmtree(bg, ignore_errors=True)
        if n >= max_per:
            break
(out / "mined.json").write_text(json.dumps(kept, indent=1))
print(len(kept), "pairs kept")
