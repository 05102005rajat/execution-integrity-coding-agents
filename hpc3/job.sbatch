#!/bin/bash
# Submit with, for example:
#   sbatch --export=ALL,MODEL=qwen3.5:2b,FAULT=stale_pyc,OUT=q35-2b-pyc job.sbatch
#   sbatch --export=ALL,MODEL=qwen3.5:2b,REALBUG=1,OUT=q35-2b-bug job.sbatch   (real-bug control)
# Optional: RUNS (default 5), SEED (default 400), TASKS (space separated, default all).
#SBATCH -p free-gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --time=2-00:00:00
#SBATCH --requeue
#SBATCH -J exp1
#SBATCH -o exp1-%j.out
set -u
export PATH="$HOME/ollama/bin:$HOME/venv/bin:$PATH"
export OLLAMA_MODELS="$HOME/ollama_models"
PORT=$((20000 + RANDOM % 20000))
export OLLAMA_HOST=127.0.0.1:$PORT      # a random port, because nodes are shared
echo "node: $(hostname)"; nvidia-smi -L
ollama serve > "ollama-$SLURM_JOB_ID.log" 2>&1 &
SERVER=$!
for i in $(seq 1 40); do curl -s "$OLLAMA_HOST" >/dev/null && break; sleep 2; done
cd "$HOME/exp1"
FAULT_ARGS=()
if [ -n "${FAULT:-}" ]; then FAULT_ARGS=(--fault "$FAULT"); elif [ -n "${REALBUG:-}" ]; then FAULT_ARGS=(--real-bug); fi
TASK_ARGS=()
if [ -n "${TASKS:-}" ]; then TASK_ARGS=(--tasks $TASKS); fi
# The free queue can cancel a running job to make room. On the shutdown signal, resubmit this same job; --resume skips the
# episodes that already finished, so no work is repeated.
resubmit() {
  echo "got a shutdown signal at $(date); resubmitting"
  kill $PY 2>/dev/null; kill $SERVER 2>/dev/null
  sbatch -J "$SLURM_JOB_NAME" --export=ALL "$HOME/exp1/hpc3/job.sbatch"
  exit 0
}
trap resubmit TERM
python3 run.py --agent ollama --model "$MODEL" --no-think --mode post-repair "${FAULT_ARGS[@]}" \
    --max-steps "${MAXSTEPS:-15}" --runs "${RUNS:-5}" --seed "${SEED:-400}" "${TASK_ARGS[@]}" --resume --out "results/${OUT:-run}" &
PY=$!
wait $PY
STATUS=$?
kill $SERVER 2>/dev/null
echo "run.py exit status: $STATUS"
exit $STATUS
