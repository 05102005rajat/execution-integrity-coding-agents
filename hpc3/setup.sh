#!/bin/bash
# One-time setup on HPC3, run from your home folder. Run it on the data transfer node (ssh access-hpc3.rcic.uci.edu),
# which is meant for downloads. Nothing here needs admin rights; everything goes under $HOME.
set -e
cd "$HOME"
mkdir -p ollama ollama_models

# 1. Ollama binary
if [ ! -x ollama/bin/ollama ]; then
  curl -fL https://ollama.com/download/ollama-linux-amd64.tar.zst -o ollama/ollama.tar.zst
  if command -v zstd >/dev/null; then
    (cd ollama && zstd -d -c ollama.tar.zst | tar x)
  else
    echo "zstd is not installed here. Tell Claude; there is a fallback." ; exit 1
  fi
  rm -f ollama/ollama.tar.zst
fi
ls ollama/bin/ollama

# 2. Python environment with pytest (the harness uses it)
if [ ! -d venv ]; then python3 -m venv venv; fi
./venv/bin/pip install --quiet pytest

# 3. Pull the models (a short-lived server on a spare port; no GPU is needed to download)
export OLLAMA_MODELS="$HOME/ollama_models"
export OLLAMA_HOST=127.0.0.1:21999
./ollama/bin/ollama serve > ollama_setup.log 2>&1 &
SERVER=$!
for i in $(seq 1 30); do curl -s "$OLLAMA_HOST" >/dev/null && break; sleep 2; done
for m in qwen3.5:2b qwen3.5:4b; do ./ollama/bin/ollama pull "$m" || echo "PULL FAILED: $m"; done
kill $SERVER
echo "models:"; ls ollama_models
df -h "$HOME" | tail -1
