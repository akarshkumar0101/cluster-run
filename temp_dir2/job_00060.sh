#!/bin/bash
BASH_PID=$$
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/job_00060_bash.pid

source /Users/akarshkumar0101/.virtualenvs/synthetic-mdps/bin/activate
cd /Users/akarshkumar0101/synthetic-mdps/src
python icl_bc.py --load_dir="../data/exp_icl//train_bc/name=SpaceInvaders-MinAtar"                                             --save_dir="../data/exp_icl//test_bc/name=SpaceInvaders-MinAtar/name=SpaceInvaders-MinAtar"                                             --n_iters=100 --dataset_path="../data/exp_icl//datasets//real/minatar/name=SpaceInvaders-MinAtar//dataset.pkl" --save_agent=False &> /Users/akarshkumar0101/cluster-run/temp_dir2/job_00060.log &

PYTHON_PID=$!
echo $PYTHON_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/job_00060_python.pid
echo $PYTHON_PID >> /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_freeman-titanxp-1:0.pids
wait $PYTHON_PID
RETURN_CODE=$?
echo $RETURN_CODE > /Users/akarshkumar0101/cluster-run/temp_dir2/job_00060.return

