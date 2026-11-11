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

# flask-admin (added 2026-11-10): clean = 1257e013 (fix: restore ItemsRequired validation for multi-select relations),
# bug = its parent plus the fix's test file flask_admin/tests/sqla/test_form.py. Tests live INSIDE the package; the no-tests arm
# removes flask_admin/tests from the agent's copy and grades with flask_admin/tests/sqla/test_form.py (needs a venv with
# flask wtforms sqlalchemy flask-sqlalchemy flask-babel pytest beautifulsoup4 sqlalchemy-utils psycopg2-binary arrow colour).
# git clone https://github.com/pallets-eco/flask-admin.git; git archive 1257e013 | tar x -C variants/fa-clean
# git archive 1257e013^ | tar x -C variants/fa-bug; git show 1257e013:flask_admin/tests/sqla/test_form.py > variants/fa-bug/flask_admin/tests/sqla/test_form.py

# Size ladder (2026-11-10): bs1/bs5/bs15 = boltons clean restricted to an import-closed set of modules (3.4k / 6.0k / 12.2k lines),
# with only the matching upstream tests (80 / 112 / 321 pass). Built by a short python snippet (see hypothesis_sheet.md, SIZE LADDER).
