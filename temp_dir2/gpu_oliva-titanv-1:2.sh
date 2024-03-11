#!/bin/bash
BASH_PID=$$
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:2_bash.pid
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:2.pids

export CUDA_VISIBLE_DEVICES=2
export XLA_PYTHON_CLIENT_MEM_FRACTION=.95
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00003.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00015.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00027.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00039.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00051.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00063.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:2.finish
