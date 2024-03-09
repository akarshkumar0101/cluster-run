#!/bin/bash
BASH_PID=$$
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_torralba-titanv-1:0_bash.pid

export CUDA_VISIBLE_DEVICES=0
export XLA_PYTHON_CLIENT_MEM_FRACTION=.95
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00009.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00021.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00033.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00045.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00057.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_torralba-titanv-1:0.finish
