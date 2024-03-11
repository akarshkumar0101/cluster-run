#!/bin/bash
BASH_PID=$$
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:3_bash.pid
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:3.pids

export CUDA_VISIBLE_DEVICES=3
export XLA_PYTHON_CLIENT_MEM_FRACTION=.95
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00004.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00016.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00028.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00040.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00052.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:3.finish
