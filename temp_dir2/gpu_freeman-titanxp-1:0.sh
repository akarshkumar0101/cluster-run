#!/bin/bash
BASH_PID=$$
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_freeman-titanxp-1:0_bash.pid

export CUDA_VISIBLE_DEVICES=0
export XLA_PYTHON_CLIENT_MEM_FRACTION=.95
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00000.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00012.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00024.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00036.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00048.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00060.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_freeman-titanxp-1:0.finish
