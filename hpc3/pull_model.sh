#!/bin/bash
# Usage: sbatch -p free --time=01:00:00 --cpus-per-task=2 --mem=8G hpc3/pull_model.sh MODEL_TAG
set -e
export OLLAMA_MODELS="$HOME/ollama_models"
export OLLAMA_HOST=127.0.0.1:21998
"$HOME/ollama/bin/ollama" serve > "$HOME/ollama_pull.log" 2>&1 &
SERVER=$!
for i in $(seq 1 30); do curl -s "$OLLAMA_HOST" >/dev/null && break; sleep 2; done
"$HOME/ollama/bin/ollama" pull "$1"
"$HOME/ollama/bin/ollama" show "$1" | head -12
kill $SERVER
df -h "$HOME" | tail -1
