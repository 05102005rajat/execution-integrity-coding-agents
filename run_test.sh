#!/bin/zsh
# 2-task Gemini test (leap, roman; clean + injected). Needs GEMINI_API_KEY exported in this shell.
cd ~/Desktop/exp1 || exit 1
[ -n "$GEMINI_API_KEY" ] || { echo "GEMINI_API_KEY not set"; exit 1; }
python3 run.py \
  --agent gemini \
  --model gemini-2.5-flash \
  --mode post-repair \
  --tasks leap roman \
  --runs 1 \
  --sandbox \
  --out results/gemini-post-v2
