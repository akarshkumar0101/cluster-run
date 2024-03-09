#!/bin/bash
BASH_PID=$$
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:6_bash.pid

export CUDA_VISIBLE_DEVICES=6
export XLA_PYTHON_CLIENT_MEM_FRACTION=.95
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00007.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00019.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00031.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00043.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00055.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:6.finish
