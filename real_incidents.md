# Real cases where a failing test does not mean the code is wrong

Collected 2026-10-29 for Eric's question: when would an agent see a misleading failure that a rerun does not fix? Only things I actually found are listed. Nothing here measures how often it happens.

## Stale or shadowing copies of the code (the failure repeats on every run)
- **Non-editable install shadows the source.** pytest imports whichever copy Python finds first, and a regular `pip install .` leaves a frozen copy in site-packages. pytest's own guide covers it: [Good Integration Practices](https://docs.pytest.org/en/7.1.x/goodpractices.html). Concrete reports: [pyhf, pytest fails for source installs that do not use editable mode](https://lightrun.com/answers/scikit-hep-pyhf-pytest-fails-for-source-installs-that-dont-use-pip-install---editable-) and [python3-pip-skeleton issue 98, "Non-editable test doesn't act as we think"](https://github-redirect.dependabot.com/DiamondLightSource/python3-pip-skeleton/issues/98).
- **Stale compiled bytecode, timestamp mode.** CPython itself can reuse stale bytecode when a source file is edited twice in the same second with the same size: [CPython issue 31772](https://bugs.python.org/issue31772). So my first stale-cache fault (forged timestamp) has a documented real mechanism, which I had called too rare. It is rare, not impossible.
- **Stale compiled bytecode, unchecked-hash mode.** [PEP 552](https://peps.python.org/pep-0552/) added cache files that Python never checks against the source. A Python forum thread says this can make source edits get silently ignored: [discussion on installed-module layout](https://discuss.python.org/t/pysource-file-layout-for-installed-modules/14594). Reproducible builds are why this mode exists. I verified on my own machine that an edit is ignored in this mode. I did not find a report of it hitting a Docker image; that link is my inference.
- **A passing suite for the wrong reason.** A lingering `.pyc` kept a test suite passing after the source moved: [bug report](https://www.python.org/pipermail/python-bugs-list/2011-December/154056.html).

## What the agent literature says (related, not the same question)
- A study of SWE-Agent and OpenHands failures reports that most failures reach the right function and still end with a wrong patch, with a pattern where the agent reaches correct code and then overwrites it: [arXiv 2603.24631](https://arxiv.org/abs/2603.24631). That supports the damage we see, but it is not about misleading environments.
- A preprint reports agents compromising environment integrity in a large share of cases: [arXiv 2610.18206](https://www.opentrain.ai/papers/swe-misbehavior-benchmarking-and-mitigating-boundary-violations-in-software-codi--arxiv-2610.18206/). Treat as unverified until I read the paper itself.

## What I did not find
No study that measures how often a coding agent edits correct code because a reproducible, environment-caused failure misled it. The "agents blame the code for an environment problem" pattern appears only in practitioner commentary. That is the gap, and also the main risk: it is hard to say how common the faults are in real agent runs.

## Caveats
- Several sources are forum posts, issue trackers and a blog, not peer-reviewed. The two arXiv entries I have not read beyond the summaries.
- A secondary point worth keeping: deleting `__pycache__` does not help if a long-running process still holds the old module. Our experiment does not cover that.
