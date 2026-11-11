#!/bin/sh
# Rebuilds EVERYTHING the Claude Code real-project experiments need, in a folder that survives reboots (the old /tmp scratch was wiped on 2026-11-10 23:35).
# Usage: sh real_projects/rebuild_all.sh WORKDIR        (e.g. ~/Desktop/exp1-work; must NOT be inside a git repo)
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
W=${1:?workdir}; mkdir -p "$W/variants" "$W/runs"; cd "$W"
[ -d more-itertools ] || git clone -q https://github.com/more-itertools/more-itertools.git
[ -d boltons ] || git clone -q https://github.com/mahmoud/boltons.git
[ -d flask-admin ] || git clone -q https://github.com/pallets-eco/flask-admin.git
mk() { repo=$1; F=$2; name=$3; testfile=$4; rm -rf variants/$name-clean variants/$name-bug
  (cd $repo && git archive --format=tar --prefix=$name-clean/ $F) | tar xf - -C variants
  (cd $repo && git archive --format=tar --prefix=$name-bug/ $F^) | tar xf - -C variants
  (cd $repo && git show $F:$testfile) > variants/$name-bug/$testfile; }
mk more-itertools f51a53b mit tests/test_more.py
mk boltons c1c25da bolt tests/test_mathutils.py
rm -f variants/bolt-clean/tests/test_socketutils.py variants/bolt-bug/tests/test_socketutils.py
mk flask-admin 1257e013 fa flask_admin/tests/sqla/test_form.py
python3 "$HERE/make_ladder.py" variants
[ -d venv ] || python3 -m venv venv
./venv/bin/pip install -q flask wtforms sqlalchemy flask-sqlalchemy flask-babel pytest beautifulsoup4 sqlalchemy-utils psycopg2-binary arrow colour 2>&1 | grep -v notice || true
echo REBUILD_DONE
