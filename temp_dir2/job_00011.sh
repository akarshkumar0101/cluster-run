#!/bin/bash
BASH_PID=$$
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/job_00011_bash.pid

source /Users/akarshkumar0101/.virtualenvs/synthetic-mdps/bin/activate
cd /Users/akarshkumar0101/synthetic-mdps/src
python icl_bc.py --load_dir="../data/exp_icl//train_bc/name=csmdp;i_d=1;i_s=3;t_a=3;t_c=3;t_l=0;t_s=1;o_d=1;o_c=1;r_c=0;tl=64" --save_dir="../data/exp_icl//test_bc/name=Acrobot-v1/name=csmdp;i_d=1;i_s=3;t_a=3;t_c=3;t_l=0;t_s=1;o_d=1;o_c=1;r_c=0;tl=64"            --n_iters=100 --dataset_path="../data/exp_icl//datasets//real/classic/name=Acrobot-v1//dataset.pkl"            --save_agent=False &> /Users/akarshkumar0101/cluster-run/temp_dir2/job_00011.log &

PYTHON_PID=$!
echo $PYTHON_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/job_00011_python.pid
echo $PYTHON_PID >> /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_torralba-titanv-1:4.pids
wait $PYTHON_PID
RETURN_CODE=$?
echo $RETURN_CODE > /Users/akarshkumar0101/cluster-run/temp_dir2/job_00011.return

