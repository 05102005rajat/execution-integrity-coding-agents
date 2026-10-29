# Running the experiment on HPC3 (free-gpu queue)

Facts checked on the cluster 2026-10-28: free-gpu has V100 (4 per node), A30 (4) and A100 (2) cards, 3 day limit, open to all
accounts, home folder is 50 GB. Free-queue jobs can be killed to make room for others, so job.sbatch uses --requeue and the
harness uses --resume (finished episodes are kept).

Order of steps (you do the logins; Claude cannot enter passwords or approve Duo):
1. On the Mac: scp the harness zip to HPC3 (password + Duo prompt).
2. On HPC3: unzip it, run setup.sh on the data transfer node.
3. Run a tiny test job first, read the log, then the real jobs.
