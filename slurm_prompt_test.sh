#!/bin/bash
#SBATCH --job-name=testPromptSelection
#SBATCH --account=f202500017aivlabdeucalionx
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=3:00:00
#SBATCH --partition dev-x86

# Load only necessary modules (CUDA/NCCL/OpenMPI). Remove the global Python module.
ml OpenMPI/5.0.3-GCC-13.3.0 CUDA/11.8.0 NCCL/2.20.5-GCCcore-13.3.0-CUDA-12.4.0

which python

source /projects/F202500017AIVLABDEUCALION/davibsantos/gpt_struct_me_participants/venv_39/bin/activate

python3.9 -m experiments.prompt_selection --mid qwen3_4b --language portuguese

