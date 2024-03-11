#!/bin/bash
BASH_PID=$$
echo $BASH_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/job_00025_bash.pid

source /Users/akarshkumar0101/.virtualenvs/synthetic-mdps/bin/activate
cd /Users/akarshkumar0101/synthetic-mdps/src
python icl_bc.py --load_dir="../data/exp_icl//train_bc/name=csmdp;i_d=0;i_s=0;t_a=4;t_c=2;t_l=1;t_s=0;o_d=1;o_c=1;r_c=0;tl=64" --save_dir="../data/exp_icl//test_bc/name=DiscretePendulum-v1/name=csmdp;i_d=0;i_s=0;t_a=4;t_c=2;t_l=1;t_s=0;o_d=1;o_c=1;r_c=0;tl=64"   --n_iters=100 --dataset_path="../data/exp_icl//datasets//real/classic/name=DiscretePendulum-v1//dataset.pkl"   --save_agent=False &> /Users/akarshkumar0101/cluster-run/temp_dir2/job_00025.log &

PYTHON_PID=$!
echo $PYTHON_PID > /Users/akarshkumar0101/cluster-run/temp_dir2/job_00025_python.pid
echo $PYTHON_PID >> /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:0.pids
wait $PYTHON_PID
RETURN_CODE=$?
echo $RETURN_CODE > /Users/akarshkumar0101/cluster-run/temp_dir2/job_00025.return

