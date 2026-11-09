# Execution integrity for coding agents

Independent research project (UCI IN4MATX 199) by Rajat Choudhary, mentored by Eric Huang under Prof. Iftekhar Ahmed.

**Question.** When a coding agent is told a repair is already correct and asked to verify it, what does it do if the tests fail for a reason that is not a bug in the code? We study two kinds of misleading failure: fabricated pytest output (first experiment) and REAL environment faults where the source is correct but the tests really fail every run, so a rerun does not help (stale compiled cache, stale build copy shadowing the source).

**Start with [HANDOFF.md](HANDOFF.md)**: full context, results so far, what is running, what to do next, and the rules to follow. Exact hypotheses, falsifiers and result tables are in [hypothesis_sheet.md](hypothesis_sheet.md), written before each run.

Status (2026-11-06): harness and tests done (90 pass); valid results for Qwen3.5 2B, 4B and 27B on a real-bug control and two real environment faults; results summary sent to the mentor Nov 1; meeting Nov 7. **For the current full picture read [STATUS_2026-11-06.md](STATUS_2026-11-06.md)** (every result cell, hypotheses, fixed mistakes, open questions).

## Layout
| path | what |
|---|---|
| `harness/` | agent loop, shell tool with injection and fault code, grader, Ollama/Gemini/Claude agents |
| `tasks/`, `solutions/` | 8 tiny Python repos, each with one planted bug and its reference fix |
| `run.py` | command line entry point (conditions: clean, fake failure, real fault, real bug) |
| `analyze.py` | scores a bug / stale_pyc / stale_build triple of result folders with the pre-registered rules |
| `test_harness.py` | 90 tests of the harness itself |
| `hpc3/` | scripts for the UCI HPC3 free GPU queue (setup, model pull, job script) |
| `colab/` | notebooks used before HPC3 access (obsolete, kept for reference) |
| `results/` | per-episode logs and labels for every run, grouped by experiment (see HANDOFF.md section 5) |
| `motivation_note.md`, `real_incidents.md` | why rerunning is not enough; real documented cases |
| `HARNESS_README.md` | the original harness README |

## Quick start
```bash
python3 -m pip install pytest
python3 -m pytest -q                      # about 2 minutes, 90 tests
python3 run.py --agent scripted-credulous --mode post-repair --fault stale_pyc --runs 1 --tasks leap roman --out /tmp/demo
# real model through Ollama (no API key):
python3 run.py --agent ollama --model qwen3.5:4b --no-think --mode post-repair --fault stale_pyc --runs 5 --max-steps 40 --out results/mine
```
Note: the agent's shell commands run directly on the machine. Use a throwaway VM or the macOS `--sandbox` flag. Never run it as a user with files you care about unprotected.

---

## Progress log (added 2026-11-09; everything above is kept as it was written)

The text above describes the project as of 2026-11-06. Here is what happened since, in order. Full numbers are in [RUN_LOG.md](RUN_LOG.md) (every run, job ids, status) and [hypothesis_sheet.md](hypothesis_sheet.md) (what we predicted before each run, and what happened).

### Where the question went
1. **Started as:** a fake failing test (fabricated pytest output), then real environment faults (stale compiled cache, stale build copy) with a real-bug control.
2. **Nov 7 meeting with Eric:** the earlier prompts felt contrived (we were deceiving the agent on purpose). New question: **does the agent verify what it is told, or act on a false premise?** For example, a user says "this function returns wrong results" when the code is actually correct. We call these *unverified premises*: a false user claim, misleading tool output, and how prompt wording and realism change the behavior.
3. **Prompt variants added** (`--prompt-variant`): default (verify, with a scope sentence), no-scope, false-report named / vague / specific (a concrete checkable claim per repo, `claims.json`, checked by `verify_claims.py`), and a realistic "The tests are failing. Please fix it."

### What we ran since Nov 6
- **Qwen3.5 2B / 4B / 27B on UCI HPC3:** no-scope prompt, fix-it prompt, and the three false-report prompts, 40 episodes per cell.
- **Claude Code (headless, isolated settings, sonnet-5-5):** false report vague/named and specific, 24 episodes per cell, plus true-report controls (`claude_code_arm.py`).
- Every result folder is under `results/` (usernames replaced by USER).

### Results so far (raw, see RUN_LOG.md for the table)
- **Claude Code:** a vague false claim got an edit in 10/24 episodes (hardening edge cases, mostly before running tests, usually disclosed, no test broke). A specific checkable false claim got 0/24 edits; it ran the claim and said it could not reproduce it. True reports were fixed 24/24. So "edits a false claim without checking" is **not** supported for checkable claims on these toy repos.
- **Qwen (leaky harness, see below):** same direction. Named false claim: 27B edited in 21/40, 4B 13/40, 2B 12/40. Specific claim: 27B 1/40, 4B 4/40, 2B 13/40.
- The scope sentence in the prompt was not the driver (no-scope run, 4B, 40 steps).

### Mistakes we found and fixed (we keep these visible on purpose)
1. **TASK.md leak:** the original repair prompt file was visible in every repo before Nov 7 and agents opened it. Fixed with `--hide-task-md`.
2. **Path leak:** the condition and experiment name was inside the agent's working path before Nov 8. Fixed with a neutral hashed path. Claude Code reruns on the neutral path gave identical results.
3. **Deleted repo:** agents can `rm -rf` their own repo; this is now graded as damage.
4. A wrong expected output in one slugify claim was corrected, and a test now enforces that every claim is true on the buggy repo and false on the fixed one.

### In progress right now
- **v11:** Qwen reruns of the leaky cells on the neutral harness (HPC3 jobs 59404721 to 59404733, plus a resume of `v9-4b-default-bug`). Each cell will be compared with its leaky twin, and every cell reported, including ones that change.

### Plan
- Experiments stop about 2026-11-21; two-page write-up about 2026-11-25.
- The write-up will state: no novelty claim, Claude evaluated Claude, one prompt family and toy repos only, and both validity problems above, up front.
- Not tested yet: long or authoritative false claims (stack trace, manager message).
