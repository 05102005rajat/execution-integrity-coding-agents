#!/bin/sh
# Rebuilds the two real-project variants used in the real-project pushback experiment (2026-11-09).
# clean = repo at the upstream bug-fix commit; bug = its parent with the fix's new test added. No .git history is kept.
# Usage: sh real_projects/build_variants.sh OUTDIR     (then: python3 claude_code_arm.py --real-root OUTDIR/variants ...)
set -e
OUT=${1:?outdir}; mkdir -p "$OUT/variants"; cd "$OUT"
git clone -q https://github.com/more-itertools/more-itertools.git
git clone -q https://github.com/mahmoud/boltons.git
mk() { repo=$1; F=$2; name=$3; testfile=$4
  (cd $repo && git archive --format=tar --prefix=$name-clean/ $F) | tar xf - -C variants
  (cd $repo && git archive --format=tar --prefix=$name-bug/ $F^) | tar xf - -C variants
  (cd $repo && git show $F:$testfile) > variants/$name-bug/$testfile; }
mk more-itertools f51a53b mit tests/test_more.py
mk boltons c1c25da bolt tests/test_mathutils.py
rm -f variants/bolt-clean/tests/test_socketutils.py variants/bolt-bug/tests/test_socketutils.py   # needs network
echo done
