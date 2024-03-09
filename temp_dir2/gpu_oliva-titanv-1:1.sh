#!/bin/bash
BASH_PID=$$
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:1_bash.pid

export CUDA_VISIBLE_DEVICES=1
export XLA_PYTHON_CLIENT_MEM_FRACTION=.95
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00002.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00014.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00026.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00038.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00050.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/job_00062.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:1.finish
