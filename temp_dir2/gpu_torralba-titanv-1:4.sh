#!/bin/bash
BASH_PID=$$
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_torralba-titanv-1:4_bash.pid
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_torralba-titanv-1:4.pids

export CUDA_VISIBLE_DEVICES=4
export XLA_PYTHON_CLIENT_MEM_FRACTION=.95
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00011.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00023.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00035.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00047.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00059.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_torralba-titanv-1:4.finish
