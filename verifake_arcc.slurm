#!/bin/bash
#SBATCH --job-name=verifake-repair
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=180G
#SBATCH --time=24:00:00
#SBATCH --output=verifake_repair_%j.log

# Adapted launcher. The completed run's source hashes are preserved separately.
# Ask for permission before an experimental rerun.
# Activate the compatible environment before submission.
# Pass your account and partition to sbatch; no account is embedded here.
set -euo pipefail
cd "${SLURM_SUBMIT_DIR}"
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONUNBUFFERED=1
python repair_verifake.py --data data --previous previous_results --output verifake_repair_results --workers 8
