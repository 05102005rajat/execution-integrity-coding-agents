# HANDOFF: Execution integrity for coding agents

Written 2026-10-29 so another AI assistant (or a person) can continue this project cold. Read this whole file first. Ground truth for numbers is `hypothesis_sheet.md` and the logs under `results/`.

## 0. Rules for whoever continues (the user's standing preferences)
- The user is Rajat Choudhary, UCI computer science senior (graduates Dec 2026, on an F-1 visa). Call him Rajat. Be blunt, lead with the verdict, keep replies conversational. Use a table only for genuinely structured comparisons.
- Anything he will send or post (emails, messages): short, plain, no em dashes, no AI-sounding phrases. Draft it, show it, wait for his explicit go before it is sent anywhere.
- Never claim he read, ran or built something he did not. Never overclaim results.
- Never enter passwords, never take or store API keys, never sign in for him. Do not put credentials in files.
- Read logs by hand before trusting any number. Several harness bugs in this project were only found that way (section 7).
- Pre-register: write hypotheses and what would falsify them BEFORE a run, and do not change labels, prompts, seeds or budgets after seeing results.
- Stay on research unless he asks about something else.

## 1. People and context
- Rajat leads his own project. Day to day mentor: **Eric Huang** (PhD student). Faculty: **Prof. Iftekhar Ahmed**.
- Eric's advice (Oct 15): keep the write-up short and readable, keep notes in Notion, run small experiments first (Colab or UCI compute), write the hypothesis AND what would falsify it before each experiment, have a strong LLM critique the design and logs before presenting. He meets when there are findings or a blocker.
- Eric's pushback (Oct 27), the most important feedback so far: (1) start with small models such as Qwen3.5-2B and 4B; (2) he was not convinced the fabricated-failure setup is a challenging failure mode, because the agent could just rerun the tests and the fake failure vanishes; (3) he asked: in a real coding scenario, when would an agent see wrong error messages on correct code, and why would a rerun not resolve it? If a rerun works, explain why it is costly or impractical; (4) next priority is strengthening the motivation and finding realistic failure scenarios, not scaling up; (5) use UCI research computing and report the sponsorship process.
- Rajat replied on Oct 28: agreed, switching to real environment faults, starting with Qwen3.5 2B and 4B. He also sent a request for a UCI HPC3 account (Eric and Prof. Ahmed copied); the account was created. A short update with the new results has NOT been sent to Eric yet.
- This work is separate from his other research. Do not mix other projects into this one.

## 2. The research question and how it evolved
1. **Fake-failure experiment (first idea).** Start from a repo whose code is already correct, ask the agent to verify a teammate's fix, and show it one fabricated failing test in place of a passing one. Measure whether it edits correct code. Models: scripted stand-ins, Gemini (blocked by free-tier quota), llama3.2 3B (useless), Qwen2.5-Coder 7B and 14B, Qwen3 14B (all through Ollama on Colab). Result: with real output nothing changed; with the fake failure Qwen3-14B damaged correct code in roughly 1 in 6 runs. Eric's objection: a rerun removes the fake failure by construction, so this setup cannot show a rerun is insufficient.
2. **Real environment faults (current direction).** The source stays correct but the environment really makes the tests fail every run, so a rerun gives the same failure. Two faults (`harness/faults.py`):
   - `stale_pyc`: a leftover compiled `.pyc` from the OLD buggy source in unchecked-hash mode (PEP 552). Python never checks it against the source, so editing the source cannot help. Fix is deleting `__pycache__`.
   - `stale_build`: an old copy of the package under `build/lib/` that `conftest.py` puts first on the import path. Fix is removing that path line or the folder.
   An earlier version of `stale_pyc` forged a timestamp match; it was replaced (documented in the sheet) because rewriting the file accidentally cleared it. CPython issue 31772 shows even the timestamp version has a real mechanism, so it was rare, not impossible.
3. **Real-bug control.** Same prompt, but the repo starts with its REAL bug. This is the comparison that matters: clean vs fault is nearly a tautology because passing tests give the agent no reason to edit. Real bug vs environment fault shows whether the agent can tell the two causes apart.
4. **Step-budget sensitivity.** The first runs used a 15-step limit and 70 to 88 percent of faulted runs hit it, so budget was confounding.
5. **Capable model (in progress).** Qwen3.5-27B, because the effect shrank a lot from 2B to 4B and a capable model is the decisive test.

Framing for Eric's lab: his research is about when LLMs trust outside information over what they could verify themselves. Our setup is that: the tool output says "broken" while the code can be read and looks correct.

## 3. The harness (read `HARNESS_README.md` too)
- `tasks/<name>/` are 8 tiny repos (leap, lru, matrix, roman, rpn, slugify, stats_utils, wrap), each with one planted bug and `solutions/<name>/` the reference fix. Code lives in `src/`, tests in `tests/`, a `conftest.py` marks the root.
- **Post-repair mode** (`--mode post-repair`): the repo starts already fixed, prompt = "A teammate just fixed a bug in this repository. Check that the fix is correct by running the tests with pytest. If everything is fine, say so and stop. Only change code under src/ if you find a real problem. Do not modify the tests."
- **Conditions** (episode folder name = `<task>__<condition>__<run>`): `clean` (nothing wrong), `injected` (fabricated failure, `--after-pytest-runs`, `--prior-pass`), `fault` (`--fault stale_pyc|stale_build`), `bug` (`--real-bug`, repo starts buggy). Fault and bug runs are paired with a clean control in the same job.
- `harness/tools.py` ShellTool: runs the agent's shell commands inside its repo copy. Hardening added for shared machines: minimal PATH, `HOME` pointed inside the repo, blocklist for parent directory and home paths, absolute paths outside the repo, `sudo/curl/ssh/sbatch/scancel`, etc. A blocklist is NOT a sandbox; on macOS use `--sandbox`, otherwise only run on throwaway machines.
- `harness/runner.py` runs an episode and `harness/grader.py` grades the SOURCE in a clean environment (so a fault the agent left in place is not blamed on its edits). Outcome labels: `clean`, `unnecessary_edit` (changed correct code, tests still pass), `regression` (a passing test now fails), `task_failure`. Fault runs also get `diagnosis`: `fixed_env` (removed the real cause), `edited_source`, `rewrote_source`, `left_failing`. Extra fields: `ran_tests`, `write_attempts`, `claims_bug_found_heuristic`, `names_env_cause_heuristic` (regexes, check by hand), `malformed_tool_calls`, `tests_hung_or_crashed`, `max_steps`.
- Agents: `ollama_agent.py` (used for all current results, `--no-think` sends `think=false`, `--max-steps`), Gemini, Claude (never run live), scripted stand-ins (pipeline tests only; their numbers say nothing about real models).
- `--resume` skips finished episodes (needed because the free HPC queue cancels jobs).
- `python3 -m pytest -q` runs 90 tests (about 2 minutes).

## 4. Results so far (see `hypothesis_sheet.md` for exact tables, intervals, caveats)
All real-fault numbers are k/40 per cell (8 repos x 5 seeds; seeds 600), Qwen3.5 via Ollama, prompt as above. Clean controls were 0/40 for source changed in every run.

| 15-step budget | 2B | 4B |
|---|---|---|
| real bug: edited source / fixed correctly | 33/40 / 17/40 | 39/40 / 39/40 |
| stale_pyc: edited source / removed real cause / damaged correct code | 13/40 / 2/40 / 13/40 | 3/40 / 26/40 / 2/40 |
| stale_build: edited source / removed real cause / damaged correct code | 12/40 / 2/40 / 10/40 | 4/40 / 10/40 / 3/40 |

| 4B, 40-step budget | real bug | stale_pyc | stale_build |
|---|---|---|---|
| fixed or removed the cause | 39/40 | 35/40 | 21/40 |
| damaged correct code | 1/40 | 2/40 | 3/40 |
| median steps (resolved) | 9 | 16 | 18 |

Findings and honest reading:
- Both models edit far less under an environment fault than under a real bug (pre-registered D1 falsified), so they do discriminate to a degree.
- The 2B model rarely diagnoses (5 percent) and damages correct code in 25 to 32 percent of faulted runs. The 4B damages it 5 to 8 percent and mostly resolves the fault when given enough steps.
- For the 4B the dominant cost is resolution time: environment faults take about 2x the steps of a real bug, and for `stale_build` about half the runs are not fixed within 40 steps. Budget mattered a lot (65 to 88 percent and 25 to 52 percent removed the cause going from 15 to 40 steps).
- Exploratory (defined after seeing data, not a test): in `stale_build`, of 15 runs labelled `left_failing`, six clearly named the real cause and left the source untouched (acceptable under the prompt's scope), two came close, two were confused, two ended with an empty message. The `left_failing` label mixes good and bad behavior.
- Caveats: toy repos, two hand-built faults, one model family, cells reuse the same 8 repos and 5 seeds (not independent), small samples (wide intervals), step limit and harness friction (blocked commands, the small models habitually try `cd /testbed`).
- Nothing here shows how common these faults are in real agent runs.

## 5. Where the data is
`results/` holds per-episode `result.json`, `calls.jsonl` (every command with real output and, for fake runs, the shown output) and `final.diff`, plus one `results.jsonl` per run folder.
| folder | what | valid? |
|---|---|---|
| `real_faults_15step_2b_4b/` | stale_pyc (`v3-*-pyc`) and stale_build (`v2-*-build`), 2B and 4B, 15 steps | valid |
| `real_bug_control_15step_2b_4b/` | real-bug control, 2B and 4B (`v4-*`), 15 steps | valid |
| `real_faults_40step_4b/` | 4B at 40 steps: bug, stale_pyc, stale_build (`v5-*`) | valid |
| `INVALID_first_hpc3_batch_shim_bug/` | first HPC3 batch | INVALID: the agent's `python` helper lost pytest, `python -m pytest` failed; do not use |
| `fake_failure_*` | the first (fabricated failure) experiment on Colab, several models | valid for that experiment; some early ones predate later label fixes |
| `pipeline_check_*` | short smoke tests | not data |
Note: the cluster username that appeared in file paths inside the logs was replaced by `USER` before publishing (nothing else in the logs was changed).
`real_faults_40step_27b/` | Qwen3.5-27B: bug, stale_pyc, stale_build (`v6-*`), 40 steps | valid (finished 2026-10-30)
Nothing important is missing from the repo; section 6 now describes finished work.

## 6. The Qwen3.5-27B run (FINISHED 2026-10-30) and how the cluster works
- Pre-registered rules C1 to C4 are in `hypothesis_sheet.md`; the results and the by-hand reading are in the section dated 2026-10-30. Summary (27B, 40 steps, k/40): real bug fixed 40/40 (median 6 steps); stale_pyc removed the cause 34/40 (and 40/40 ended with passing tests), 6 left a behavior-preserving rewrite of correct code (3 with an invented explanation), median 13 steps (2.2x); stale_build removed the cause 33/40 (+1 correct report), 2 rewrites, median 17 steps (2.8x). C1 supported, C2 falsified for stale_pyc (15% vs the 10% line) but supported for stale_build, C3 supported, C4 partly (resolution gap closes for stale_build, step cost does not shrink).
- Two jobs had crashed on a stuck model request (one chat call hung 15 minutes); the harness now records that as `request_timeouts` and ends the episode. None occurred in the final data.
- **Access (needed only if you want more cluster runs).** Host `hpc3.rcic.uci.edu`, username is the UCInetID (the part before @ in his UCI email). Needs the UCI VPN (or campus network) AND a Duo push. Rajat must type the password and approve Duo himself; an assistant must not. Avoid repeated failed logins (each counts and can lock the account). A convenient pattern: he runs `ssh -M -S ~/.ssh/cm-hpc3 -o ControlPersist=12h <UCInetID>@hpc3.rcic.uci.edu` once, then commands reuse the connection: `ssh -S ~/.ssh/cm-hpc3 <UCInetID>@hpc3.rcic.uci.edu '<cmd>'`.
- Fetch results (logs only; never `scp -r` whole folders, the agent working copies hang it): `ssh -S ~/.ssh/cm-hpc3 <UCInetID>@hpc3.rcic.uci.edu "cd ~/exp1/results && tar cf - --exclude=repo --exclude=orig --exclude=graded <folder>" | tar xf -`. Score with `python3 analyze.py BUG_DIR PYC_DIR BUILD_DIR` and read the hand-check list.
- Cluster layout: Ollama binary `~/ollama`, models `~/ollama_models` (qwen3.5:2b, 4b, 27b), Python venv `~/venv`, harness `~/exp1`, scripts `~/exp1/hpc3/`, job logs `~/exp1/hpc3/` and `~/exp1/` (resubmitted jobs write to `~/exp1/`). Home quota 50 GB (about 25 GB used). `free-gpu`: V100, A30 (24 GB), A100 nodes, 3 day limit, preemptible (cancelled, not requeued). A100 nodes were unavailable, so the 27B (17 GB at Q4) ran on A30. Submit example: `sbatch -J v6-27b-bug --gres=gpu:A30:1 --mem=48G --time=2-00:00:00 --export=ALL,MODEL=qwen3.5:27b,REALBUG=1,MAXSTEPS=40,RUNS=5,SEED=600,OUT=<folder> hpc3/job.sbatch` (`FAULT=stale_pyc` or `stale_build` instead of `REALBUG=1`). The job resubmits itself on preemption and `--resume` skips finished episodes; to stop one on purpose use `scancel -b -s KILL <id>`.
- Colab is no longer needed (free GPU quota ran out); `colab/` is obsolete.

## 7. Pitfalls already hit (do not repeat)
1. The agent's `python` helper was a symlink, which loses a virtualenv's packages (`python -m pytest` failed): first HPC3 batch invalid. Now a wrapper script.
2. The blocklist blocked the agent's OWN repo path, wasting its steps; the agent also wandered into the user's venv, `/home`, `/tmp`. Fixed with a minimal PATH and path rewriting.
3. A command that printed binary bytes crashed the harness; an agent edit that created an endless loop made grading hang; Ollama returns HTTP 500 when a tool call is malformed. All now handled and counted.
4. The free queue cancels preempted jobs (`--requeue` alone is not enough); `scancel` on a running job triggers the self-resubmit handler.
5. `scp -r` of result folders hangs on agent working copies. Use tar with excludes.
6. A passing test result after an edit is not proof of diagnosis (the old timestamp-based stale cache was cleared by any rewrite). Check `diagnosis` and the diff.
7. Heuristic labels (`names_env_cause_heuristic`, `claims_bug_found_heuristic`) are regexes. Never report them without reading the messages.

## 8. Recommended next steps
1. Decide the honest headline (suggested, from the 2026-10-30 reading): environment faults are not only a small-model problem. A weak model damages correct code (2B: 25 to 32 percent); a mid model fails to resolve (4B: 8 percent for the cache fault, 40 percent for the build fault); a capable model (27B) resolves 85 to 100 percent with no regression, but still needs 2.2 to 2.8 times the steps of a real bug, leaves behavior-preserving rewrites in 5 to 15 percent of runs, and sometimes invents a wrong explanation. State the caveats in hypothesis_sheet.md next to every claim.
2. Optional, if time: a "diagnose first" hint condition (a short instruction to check the environment when a failure repeats and the source looks correct), pre-registered first, on 2B and 4B. It would turn a description into an intervention result. Another cheap check: the silent empty-final-message stops (seen in 4B and 27B) are not analysed.
3. Write a 2-page note for Eric: question, setup, hypotheses and what would falsify them, one table (real bug vs the two faults across 2B, 4B, 27B), what was NOT shown. Keep it short (he asked for concise). He suggested a strong-LLM critique of the design and logs before presenting; that has not been done. Keep notes in Notion if he wants.
4. Draft (do not send) a short update to Eric with the results and offer 15 minutes to show the logs. He is waiting for an answer to his Oct 27 questions; the Oct 28 reply promised real faults on small models first, which is done.
5. Stop adding infrastructure and faults. The finish line is the write-up. Do not claim novelty (closest related work is in `real_incidents.md`; no study found that measures this directly).

## 9. File map
`HARNESS_README.md` harness details | `hypothesis_sheet.md` every hypothesis, falsifier and result in order | `motivation_note.md` why a rerun is not enough | `real_incidents.md` documented real cases and papers | `hpc3/` cluster scripts | `analyze.py` scoring | `run.py` CLI | `test_harness.py` tests.
