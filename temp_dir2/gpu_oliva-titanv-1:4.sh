#!/bin/bash
BASH_PID=$$
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:4_bash.pid
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:4.pids

export CUDA_VISIBLE_DEVICES=4
export XLA_PYTHON_CLIENT_MEM_FRACTION=.95
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00005.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00017.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00029.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00041.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00053.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:4.finish
