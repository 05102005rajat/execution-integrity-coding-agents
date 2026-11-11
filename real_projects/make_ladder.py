#!/usr/bin/env python3
"""Builds the boltons size-ladder variants bs1/bs5/bs15 (import-closed module sets) from variants/bolt-clean. Usage: make_ladder.py VARIANTS_DIR"""
import re, pathlib, shutil, sys
root = pathlib.Path(sys.argv[1]); base = root / 'bolt-clean'
mods = {p.stem for p in (base / 'boltons').glob('*.py')}
def deps(m):
    t = (base / 'boltons' / f'{m}.py').read_text()
    return set(re.findall(r'(?:from boltons(?:\.| import )|import boltons\.|from \. import |from \.)(\w+)', t)) & mods
def closure(ms):
    ms = set(ms)
    while True:
        n = set(ms)
        for m in list(ms):
            n |= deps(m)
            for tf in (base / 'tests').glob(f'test_{m}*.py'):
                n |= set(re.findall(r'boltons\.(\w+)', tf.read_text())) & mods
        if n == ms: return ms
        ms = n
def mk(name, ms):
    ms = closure(ms); d = root / name; shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(base, d, ignore=shutil.ignore_patterns('__pycache__'))
    for f in (d / 'boltons').glob('*.py'):
        if f.stem not in ms and f.name != '__init__.py': f.unlink()
    for f in (d / 'tests').glob('test_*.py'):
        s = f.stem[5:]
        if not any(s == m or s.startswith(m) for m in ms): f.unlink()
    print(name, sorted(ms), sum(len(p.read_text().splitlines()) for p in (d / 'boltons').glob('*.py')), 'lines')
mk('bs1', ['iterutils'])
mk('bs5', ['iterutils', 'strutils', 'dictutils', 'setutils', 'listutils'])
mk('bs15', ['iterutils', 'strutils', 'dictutils', 'setutils', 'listutils', 'urlutils', 'funcutils', 'cacheutils', 'statsutils', 'tableutils', 'timeutils', 'mathutils', 'pathutils', 'jsonutils', 'typeutils'])
