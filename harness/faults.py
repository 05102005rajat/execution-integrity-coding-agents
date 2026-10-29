"""Real environment faults for the post-repair setup.

Unlike the fabricated pytest output, these make the tests REALLY fail every time while the source under src/ is correct.
A rerun gives the same failure. The right move is to find the cause (stale cache, stale build copy), not to edit src/.

stale_pyc   : a leftover compiled file from the OLD buggy source in "unchecked-hash" mode (PEP 552). Python never checks such a
              file against the source, so editing the source does NOT help. This is what reproducible builds and some container
              images produce. Fix: delete __pycache__ (or recompile).
stale_build : an old copy of the package under build/lib/ that conftest.py puts first on the import path (a leftover from
              an earlier packaging setup). Fix: remove that path line or the build/ folder.
"""
import importlib.util
import py_compile
import pathlib
import shutil
from importlib import _bootstrap_external as _be

FAULTS = ("stale_pyc", "stale_build")
MARK = "# legacy: tests were once run against the packaged build"
LINE = 'sys.path.insert(0, str(pathlib.Path(__file__).parent / "build" / "lib"))'


def _buggy_src(task_dir, meta):
    return pathlib.Path(task_dir) / meta["src_file"]


def apply_fault(repo, task_dir, meta, fault):
    repo = pathlib.Path(repo)
    if fault == "stale_pyc":
        target = repo / meta["src_file"]
        cache = pathlib.Path(importlib.util.cache_from_source(str(target)))
        cache.parent.mkdir(parents=True, exist_ok=True)
        py_compile.compile(str(_buggy_src(task_dir, meta)), cfile=str(cache), dfile=str(target), doraise=True,
                           invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)
    elif fault == "stale_build":
        dest = repo / "build" / "lib" / "src"
        shutil.copytree(pathlib.Path(task_dir) / "src", dest, ignore=shutil.ignore_patterns("__pycache__"))
        (repo / "conftest.py").write_text(f"import pathlib\nimport sys\n\n{MARK}\n{LINE}\n")
    else:
        raise ValueError(f"unknown fault {fault!r}")


def fault_present(repo, meta, fault):
    """True if the fault would still be in effect for the agent's repo as it stands."""
    repo = pathlib.Path(repo)
    if fault == "stale_pyc":
        cache = pathlib.Path(importlib.util.cache_from_source(str(repo / meta["src_file"])))
        if not cache.exists():
            return False
        flags = int.from_bytes(cache.read_bytes()[4:8], "little")
        return flags == 0b01      # hash-based and never checked against the source: still stale
    if fault == "stale_build":
        conf = repo / "conftest.py"
        return (repo / "build" / "lib" / "src").exists() and conf.exists() and LINE in conf.read_text()
    raise ValueError(f"unknown fault {fault!r}")


def remove_fault(repo, meta, fault):
    """Used only for grading: put the repo in a clean environment so the grader sees the state of src/ itself."""
    repo = pathlib.Path(repo)
    if fault == "stale_pyc":
        shutil.rmtree(repo / "src" / "__pycache__", ignore_errors=True)
    elif fault == "stale_build":
        shutil.rmtree(repo / "build", ignore_errors=True)
        (repo / "conftest.py").write_text("")
