#!/bin/bash
BASH_PID=$$
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:0_bash.pid
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:0.pids

export CUDA_VISIBLE_DEVICES=0
export XLA_PYTHON_CLIENT_MEM_FRACTION=.95
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00001.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00013.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00025.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00037.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00049.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00061.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:0.finish
