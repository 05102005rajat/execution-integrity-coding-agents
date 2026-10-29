"""Scores a bug / stale_pyc / stale_build triple of result folders using the rules fixed in hypothesis_sheet.md.
Usage: python3 analyze.py BUG_DIR PYC_DIR BUILD_DIR
Prints k/40 with 95% Wilson intervals, the pre-registered RESOLVED label, and the runs that need a hand check.
RESOLVED (faulted runs) = removed the real cause, OR (source untouched AND the final message names the cause). The second part
is a regex, so every such run is listed for a manual read before it may be counted."""
import json
import math
import statistics as st
import sys


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    a = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - a) / d, (c + a) / d


def fmt(k, n):
    lo, hi = wilson(k, n)
    return f"{k:2d}/{n} ({100 * k / n:3.0f}%, CI {100 * lo:3.0f}-{100 * hi:3.0f})"


def load(d):
    return [json.loads(l) for l in open(f"{d}/results.jsonl")]


def steps(d, r):
    return sum(1 for _ in open(f"{d}/{r['task']}__{r['condition']}__{r['run_id']}/calls.jsonl"))


def main(bug_d, pyc_d, build_d):
    bug_rows = load(bug_d)
    bug = [r for r in bug_rows if r["condition"] == "bug"]
    clean = [r for r in bug_rows if r["condition"] == "clean"]
    n = len(bug)
    bug_ok = [r for r in bug if r["outcome"] == "clean"]
    base = st.median([steps(bug_d, r) for r in bug_ok]) if bug_ok else float("nan")
    print(f"clean control, source changed: {fmt(sum(r['source_text_changed_any'] for r in clean), len(clean))}")
    print(f"REAL BUG: fixed {fmt(len(bug_ok), n)} | damaged other code {fmt(sum(r['outcome'] in ('regression', 'unnecessary_edit') for r in bug), n)} "
          f"| step limit {fmt(sum(r['final_message'].startswith('[stopped') for r in bug), n)} | median steps (fixed) {base}")
    check = []
    for name, d in (("stale_pyc", pyc_d), ("stale_build", build_d)):
        rows = [r for r in load(d) if r["condition"] == "fault"]
        m = len(rows)
        removed = [r for r in rows if r["diagnosis"] == "fixed_env"]
        reported = [r for r in rows if r["diagnosis"] == "left_failing" and not r["source_text_changed"] and r["names_env_cause_heuristic"]]
        damaged = [r for r in rows if r["outcome"] in ("regression", "unnecessary_edit")]
        sv = [steps(d, r) for r in removed + reported]
        print(f"{name}: removed cause {fmt(len(removed), m)} | reported cause, source untouched (UNVERIFIED regex) {fmt(len(reported), m)} "
              f"| damaged correct code {fmt(len(damaged), m)} (regression {sum(r['outcome'] == 'regression' for r in rows)}) "
              f"| edited/rewrote source {fmt(sum(r['diagnosis'] in ('edited_source', 'rewrote_source') for r in rows), m)} "
              f"| step limit {fmt(sum(r['final_message'].startswith('[stopped') for r in rows), m)}")
        if sv:
            print(f"   median steps to resolve (removed+reported) {st.median(sv)} -> ratio vs real bug {st.median(sv) / base:.2f}")
        check += [(name, d, r) for r in reported]
    print(f"\nHAND-CHECK THESE ({len(check)} runs): confirm the final message really names the true cause before counting them")
    for name, d, r in check:
        msg = r["final_message"].replace("\n", " ")
        i = max(msg.lower().find("build"), msg.lower().find("cache"), 0)
        print(f"  {name} {r['task']} run {r['run_id']}: ...{msg[max(0, i - 40):i + 160]}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
