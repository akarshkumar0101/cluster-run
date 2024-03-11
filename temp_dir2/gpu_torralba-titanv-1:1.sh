#!/bin/bash
BASH_PID=$$
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_torralba-titanv-1:1_bash.pid
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_torralba-titanv-1:1.pids

export CUDA_VISIBLE_DEVICES=1
export XLA_PYTHON_CLIENT_MEM_FRACTION=.95
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00010.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00022.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00034.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00046.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00058.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_torralba-titanv-1:1.finish
