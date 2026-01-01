#!/bin/bash
#SBATCH --job-name=qwen38bbeventtype
#SBATCH --account=f202500017aivlabdeucaliong
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=4:00:00
#SBATCH --partition normal-a100-40

# Load only necessary modules (CUDA/NCCL/OpenMPI). Remove the global Python module.
ml OpenMPI/5.0.3-GCC-13.3.0 CUDA/11.8.0 NCCL/2.20.5-GCCcore-13.3.0-CUDA-12.4.0 Python/3.9.5-GCCcore-10.3.0

export PYTHONPATH=/projects/F202500017AIVLABDEUCALION/davibsantos/gpt_struct_me_participants/.venv/lib/python3.9/site-packages:$PYTHONPATH

source /projects/F202500017AIVLABDEUCALION/davibsantos/gpt_struct_me_participants/venv_39/bin/activate

python3.9 -m experiments.test --mid gemini --language portuguese
#python3.9 -m experiments.test --mid gemma3_1b --language portuguese
