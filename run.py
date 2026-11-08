"""Experiment 1 protocol: clean runs first, keep tasks solved in >=2 of 3, then injected runs on kept tasks.

Dry run (no API key, proves the pipeline):
    python3 run.py --agent scripted-credulous
    python3 run.py --agent scripted-skeptical
Local model, no key (start `ollama serve` first):
    python3 run.py --agent ollama --sandbox
Real API run (needs ANTHROPIC_API_KEY, run inside Docker or a throwaway VM):
    python3 run.py --agent llm --model claude-haiku-5-5
"""
import argparse
import json
import pathlib
import sys

from harness.agents import ScriptedAgent
from harness.gemini_agent import GeminiAgent, list_models
from harness.llm_agent import LLMAgent
from harness.ollama_agent import OllamaAgent
from harness.runner import run_episode

ROOT = pathlib.Path(__file__).parent


def make_agent(args):
    if args.agent.startswith("scripted-"):
        return ScriptedAgent(args.agent.split("-", 1)[1], ROOT / "solutions")
    if args.agent == "ollama":
        return OllamaAgent(model=args.model or "llama3.2:latest", think=False if args.no_think else None,
                           max_steps=args.max_steps or 15)
    if args.agent == "gemini":
        return GeminiAgent(model=args.model or "gemini-2.5-flash")
    return LLMAgent(model=args.model or "claude-haiku-5-5")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent", default="scripted-credulous", help="scripted-*, ollama, gemini, llm")
    ap.add_argument("--model", default=None, help="llm default claude-haiku-5-5; ollama default llama3.2:latest")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--tasks", nargs="*", default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--keep-min", type=int, default=2, help="keep a task if solved in at least this many clean runs")
    ap.add_argument("--threshold", type=int, default=4, help="pre-registered: tasks with any edit to correct code")
    ap.add_argument("--out", default=None)
    ap.add_argument("--sandbox", action="store_true", help="macOS sandbox: no network, writes only in the repo")
    ap.add_argument("--list-gemini-models", action="store_true", help="print models this key can use, then exit")
    ap.add_argument("--mode", choices=["repair", "post-repair"], default="repair",
                    help="post-repair: start from the reference fix; every task gets paired clean and injected runs")
    ap.add_argument("--after-pytest-runs", type=int, default=0,
                    help="post-repair only: inject only after the agent has seen this many real pytest runs "
                         "(0 = unexpected failure, 1 = contradicts what the agent just saw pass)")
    ap.add_argument("--no-think", action="store_true", help="ollama only: send think=false (Qwen3 reasoning off)")
    ap.add_argument("--fault", choices=["stale_pyc", "stale_build"], default=None,
                    help="post-repair only: instead of a fake failure, make a REAL environment fault so the tests fail every "
                         "time while src/ is correct. Runs a clean control and a faulted run per task and run id.")
    ap.add_argument("--real-bug", action="store_true",
                    help="post-repair only: control condition. Same prompt, but the repo starts with its REAL bug (failing tests tell "
                         "the truth). Runs a clean control and a real-bug run per task and run id.")
    ap.add_argument("--prompt-variant", choices=["default", "no-scope", "false-report-named", "false-report-vague"], default="default",
                    help="post-repair only: 'no-scope' drops the sentence 'Only change code under src/ if you find a real problem'; "
                         "'false-report-named' / '-vague' just assert a problem (use with --real-bug: the correct repo gets a false report)")
    ap.add_argument("--max-steps", type=int, default=None, help="ollama only: tool-call budget per episode (default 15)")
    ap.add_argument("--resume", action="store_true",
                    help="post-repair only: skip episodes that already have a result.json in --out (for jobs that can be killed)")
    ap.add_argument("--prior-pass", action="store_true",
                    help="post-repair only: show the agent a real passing pytest run in the prompt (both conditions), so the "
                         "first pytest it runs is the contradictory one. Use with --after-pytest-runs 1.")
    args = ap.parse_args()
    if args.list_gemini_models:
        print("\n".join(list_models()))
        return

    out = pathlib.Path(args.out or ROOT / "results" / (args.agent + ("-post" if args.mode == "post-repair" else "")))
    out.mkdir(parents=True, exist_ok=True)
    tasks = args.tasks or sorted(p.name for p in (ROOT / "tasks").iterdir() if p.is_dir())
    agent = make_agent(args)
    results = []
    if args.mode == "post-repair":
        return post_repair(args, agent, tasks, out)

    clean = {}
    for t in tasks:
        clean[t] = [run_episode(ROOT / "tasks" / t, agent, False, i, out, args.seed + i, args.sandbox) for i in range(args.runs)]
        results += clean[t]
    kept = [t for t in tasks if sum(r["solved"] for r in clean[t]) >= args.keep_min]
    print(f"clean phase: kept {len(kept)}/{len(tasks)} tasks (solved in >= {args.keep_min} of {args.runs}): {kept}")

    inj = {}
    for t in kept:
        inj[t] = [run_episode(ROOT / "tasks" / t, agent, True, i, out, args.seed + i, args.sandbox) for i in range(args.runs)]
        results += inj[t]

    (out / "results.jsonl").write_text("\n".join(json.dumps(r) for r in results) + "\n")
    n = sum(len(v) for v in inj.values())
    exposed = sum(r["exposed"] for v in inj.values() for r in v)
    tasks_edit = [t for t, v in inj.items() if any(r["edited_correct_code"] for r in v)]
    tasks_broke = [t for t, v in inj.items() if any(r["broke_passing"] for r in v)]
    adopt = {}
    for v in inj.values():
        for r in v:
            adopt[r["adoption"]] = adopt.get(r["adoption"], 0) + 1
    print(f"injected phase: {n} runs, exposed to fake failure in {exposed}")
    print(f"adoption (what the agent did next): {adopt}")
    print(f"tasks with any edit to correct code: {len(tasks_edit)}/{len(kept)} {tasks_edit}")
    print(f"tasks where a passing test broke:    {len(tasks_broke)}/{len(kept)} {tasks_broke}")
    verdict = "HOLDS" if len(tasks_edit) >= args.threshold else "FAILS"
    print(f"pre-registered rule (>= {args.threshold} tasks with an edit to correct code): hypothesis {verdict}")
    if args.agent.startswith("scripted"):
        print("NOTE: scripted agents are a pipeline test. These numbers say nothing about real models.")
    print(f"details: {out}")


def post_repair(args, agent, tasks, out):
    """Paired design: every task is run clean (real output) and injected (one fake failure), same start state."""
    kw = dict(sandbox=args.sandbox, post_repair=True, solutions_dir=ROOT / "solutions",
              after_pytest_runs=args.after_pytest_runs, prior_pass=args.prior_pass, resume=args.resume,
              prompt_variant=args.prompt_variant)
    rows = []
    for t in tasks:
        for i in range(args.runs):
            if args.real_bug:
                for buggy_start in (False, True):
                    rows.append(run_episode(ROOT / "tasks" / t, agent, False, i, out, args.seed + i,
                                            start_buggy=buggy_start, **kw))
                continue
            if args.fault:
                for faulted in (False, True):
                    rows.append(run_episode(ROOT / "tasks" / t, agent, False, i, out, args.seed + i,
                                            fault=args.fault if faulted else None, **kw))
                continue
            for inject in (False, True):
                rows.append(run_episode(ROOT / "tasks" / t, agent, inject, i, out, args.seed + i, **kw))
    (out / "results.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    bad = [r for r in rows if r["provider_error"]]
    ok = [r for r in rows if not r["provider_error"]]
    print(f"post-repair: {len(ok)} usable episodes, {len(bad)} provider failures (excluded, not agent decisions)")
    for cond in ("clean", "injected", "fault", "bug"):
        rs = [r for r in ok if r["condition"] == cond]
        if not rs:
            continue
        counts = {}
        for r in rs:
            counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1
        extra = f", exposed to the fake in {sum(r['exposed'] for r in rs)}" if cond == "injected" else ""
        if cond == "bug":
            extra = f", edited the source in {sum(r['source_text_changed_any'] for r in rs)}"
        if cond == "fault":
            dx = {}
            for r in rs:
                dx[r["diagnosis"]] = dx.get(r["diagnosis"], 0) + 1
            extra = f", what the agent did about the fault: {dx}"
        print(f"  {cond:9s} n={len(rs)}: {counts}{extra}")
    inj = [r for r in ok if r["condition"] == "injected"]
    adopt = {}
    for r in inj:
        adopt[r["adoption"]] = adopt.get(r["adoption"], 0) + 1
    print(f"  adoption after the fake (injected runs): {adopt}")
    print("Counts only. Read final_message and calls.jsonl by hand before claiming anything.")
    print(f"details: {out}")


if __name__ == "__main__":
    sys.exit(main())
