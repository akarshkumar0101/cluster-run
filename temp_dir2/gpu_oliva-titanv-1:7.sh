#!/bin/bash
BASH_PID=$$
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:7_bash.pid
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:7.pids

export CUDA_VISIBLE_DEVICES=7
export XLA_PYTHON_CLIENT_MEM_FRACTION=.95
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00008.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00020.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00032.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00044.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00056.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:7.finish
