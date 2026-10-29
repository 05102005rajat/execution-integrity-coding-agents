# When a rerun does not fix a misleading test failure

Rajat Choudhary, IN4MATX 199. Draft for Eric, 2026-10-28.

## The question
Eric's point: in my first experiment the fake failure appears once, so rerunning the tests removes it. That is true, and it means the experiment cannot show anything about reruns. This note lists realistic cases where a failing test is reproducible but is not evidence that the code is wrong, so a plain rerun gives the same answer.

## Cases where a rerun does not help
1. **Stale installed copy.** The package was installed earlier (pip install), so the tests import the old copy, not the folder the agent is editing. The agent fixes the source, the tests still fail, and they fail the same way every time. The right move is to check which copy is being imported. Editing correct source is the wrong move.
2. **Wrong environment.** A different interpreter, a missing or outdated dependency, or the wrong working directory. The failure repeats on every run.
3. **Stale build or cache.** Generated files, compiled output or cached results from before the edit. Same repeat failure.
4. **Flaky or order-dependent tests.** Here a rerun can help, but one passing rerun does not prove the first failure was fake, and the agent has to decide how many reruns are enough. Google reported about 16 percent of its tests showing some flakiness ([Google Testing Blog, 2017](https://testing.googleblog.com/2017/04/)).

## When reruns are costly
On large suites a full rerun can take minutes or longer, and an agent may run tests after every edit. I have not measured this, so I would not rely on cost as the main argument.

## What already exists
- Agents often struggle with environment setup itself ([SetupBench](https://arxiv.org/abs/2507.09063), [EnConda-Bench](https://arxiv.org/abs/2510.25694)). Those papers study setup, not what an agent does to correct code when the environment misleads it.
- Practitioner posts describe agents treating a red test as ground truth and reverting correct changes ([example](https://tianpan.co/blog/2026/07/02/flaky-tests-poison-agent-loops)). These are opinion pieces with no measurements.
- I did not find a study that measures how often a coding agent damages correct code because of a misleading but reproducible test failure. That is the gap, and I may have missed something.

## What I would test
Build cases 1 to 3 as real faults in the small repos, not fabricated output. For each, measure whether the agent (a) edits correct source, (b) investigates the environment, or (c) gives up. Use a rerun-first instruction as one condition: it should fail to help, because the failure repeats. Compare with an instruction to check the environment first. Hypotheses and what would prove them wrong go in the sheet before any run.

## Already seen, and what it does not show
In the fake-failure pilot (two 14B models), agents edited before rerunning in about 37 of 40 runs, so rerun-first is not their default. That says nothing yet about the cases above.

## Not claiming
These are toy repos and two small open models. Nothing here shows how often real agents hit these cases.
