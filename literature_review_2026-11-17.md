# Literature check, 2026-11-17

Source: a ChatGPT web search (run in the browser, Medium thinking) with a blunt, cite-or-say-unverified prompt, then my own check of the one paper that matters. Status of each item is marked. Anything marked UNVERIFIED comes from ChatGPT only and has not been opened by me.

## Verdict
The general finding "coding agents edit code that is already correct" is NOT new. Claude Code is in that paper's own test set. The reproduce-first result is also not new. What this repo can still add is narrower (see the end).

## Closest prior work (VERIFIED by me against arXiv)
Gloaguen, Mundler, Muller, Raychev, Vechev (ETH Zurich, LogicStar.ai). "Coding Agents Don't Know When to Act." arXiv 2605.07769, May 8 2026, ICML 2026.
- FixedBench: 200 random SWE-bench Verified instances with the golden patch already applied, so the real issue text describes a bug that is already fixed and the right move is no change. A second set (150 tasks) applies a wrong patch, so a fix is still needed.
- Agents tested: Sonnet-4.6 on Claude Code 2.1.81, GPT-5.3 Codex and GPT-5.4 mini on Codex, Gemini-3 Pro on Gemini-CLI, Qwen3.5-122B on Qwen-Code.
- Headline: 35 to 65 percent of instances get an unwanted code change.
- Table 1, resolved task, best scenario, abstention rate (higher is better), Sonnet-4.6 / GPT-5.4 mini: issue only 65.0 / 60.5; told to edit 56.5 / 36.5; reproduce first 65.5 / 47.5; reproduce then fix or abstain 80.5 / 88.5.
- Reproduce first alone helps little. Explicit permission to do nothing helps a lot. It also raises wrong abstention when a fix is still needed.
- NOT in the paper (I searched the full HTML): any multi-turn user pushback, any vague "it is not working" complaint, any comparison of checkable versus uncheckable claims. All prompts are single-shot task framings with a detailed SWE-bench issue.
- Their stated limits: Python popular repos only, no complex necessary patches, and over-abstention remains open.

## What this means for our results
- "Perfect repo, false claim, edits" is the same outcome variable as FixedBench. Do not call it a new phenomenon.
- Our reproduce-first system prompt ("reproduce first, and if you cannot, do not change code") is close to their reproduce-then-abstain condition. Our drop to 0/5 on the notes app is a replication of a known mitigation in a new setting, not a discovery.
- Different inputs: their issue text is a detailed real bug report. Ours is a vague user complaint plus up to two pushbacks, on repos that never had the bug.
- Our low edit rate on libraries (0 to 1 of 16) is below their 35 to 50 percent. Likely because our claim is vague and gives the agent nothing to patch, but that is a guess, not tested.

## Still open (per ChatGPT, consistent with my read of FixedBench)
1. Repeated user pushback versus no pushback, on the same repo. We have no no-pushback arm with matched tool use.
2. Claim the agent CAN check versus one it CANNOT. The CK1/CK2 arms are the first test of this.
3. Whether a cheap, untestable edit lever (like rewording a prompt) drives the edits.
4. Reproduce-first on unverifiable claims, where it may just force abstention. Needs a case where a real defect exists, to measure over-abstention.

## Design problems ChatGPT raised that I agree with
- Repo type and claim verifiability are confounded (library vs notes app). The CK arms keep the app fixed.
- A prompt reword is not proven harmful. Report "unsubstantiated edit", not "broke the code".
- Reproduce-first may only suppress all edits. Needs a real-bug control to show it still fixes real bugs. (Rajat's rule is no planted bugs unless he asks, so this is his call.)
- n is 5 per cell. Preliminary only.

## Other papers ChatGPT cited (UNVERIFIED by me, open before citing)
- Sharma et al. 2023, Towards Understanding Sycophancy in Language Models (ICLR 2024).
- Laban et al. 2023, Are You Sure? Challenging LLMs Leads to Performance Drops in The FlipFlop Experiment (46 percent answer flips, 17 point accuracy drop).
- Liu et al. 2025, TRUTH DECAY: Quantifying Multi-Turn Sycophancy in Language Models.
- Yao et al. 2026, Locating Sycophancy Across Training Stages in Open Language Models.
- Jimenez et al. 2023, SWE-bench. Xia et al. 2024, Agentless. OpenAI, Introducing SWE-bench Verified (38.3 percent underspecified, 61.1 percent test-quality flags).
- Meng et al. 2024, An Empirical Study on LLM-based Agents for Automated Bug Fixing.
- Guo et al. 2026, SWE-Doctor. Pan et al. 2026, Do Modifications Made by Coding Agents Make Subsequent Software Maintenance Harder. Li et al. 2026, STING mutation-guided test augmentation. Peng et al. 2026, Not All Correct Fixes Run Alike. Zheng et al. 2026, SWE-Bench Pro Verified.
- Edwards and Schuster 2026, Ask or Assume? Uncertainty-Aware Clarification-Seeking in Coding Agents. Vijayvargiya et al. 2025, Interactive Agents to Overcome Ambiguity in Software Engineering.
