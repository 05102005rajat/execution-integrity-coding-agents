# Execution integrity for coding agents

Independent research project (UCI IN4MATX 199) by Rajat Choudhary, mentored by Eric Huang under Prof. Iftekhar Ahmed.

**Question.** When a coding agent is told a repair is already correct and asked to verify it, what does it do if the tests fail for a reason that is not a bug in the code? We study two kinds of misleading failure: fabricated pytest output (first experiment) and REAL environment faults where the source is correct but the tests really fail every run, so a rerun does not help (stale compiled cache, stale build copy shadowing the source).

**Start with [HANDOFF.md](HANDOFF.md)**: full context, results so far, what is running, what to do next, and the rules to follow. Exact hypotheses, falsifiers and result tables are in [hypothesis_sheet.md](hypothesis_sheet.md), written before each run.

Status (2026-10-30): harness and tests done (90 pass); valid results for Qwen3.5 2B, 4B and 27B on a real-bug control and two real environment faults. Next step is the write-up for the mentor.

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
