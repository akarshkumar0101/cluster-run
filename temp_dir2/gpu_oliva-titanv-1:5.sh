#!/bin/bash
BASH_PID=$$
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:5_bash.pid
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:5.pids

export CUDA_VISIBLE_DEVICES=5
export XLA_PYTHON_CLIENT_MEM_FRACTION=.95
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00006.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00018.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00030.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00042.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00054.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:5.finish
