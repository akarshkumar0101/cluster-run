#!/bin/bash
touch /Users/akarshkumar0101/cluster-run/temp_dir2/job_00041.start
echo $$ > /Users/akarshkumar0101/cluster-run/temp_dir2/job_00041.start

source /Users/akarshkumar0101/.virtualenvs/synthetic-mdps/bin/activate
cd /Users/akarshkumar0101/synthetic-mdps/src
python icl_bc.py --load_dir="../data/exp_icl//train_bc/name=csmdp;i_d=0;i_s=0;t_a=4;t_c=2;t_l=1;t_s=0;o_d=1;o_c=1;r_c=0;tl=64" --save_dir="../data/exp_icl//test_bc/name=Breakout-MinAtar/name=csmdp;i_d=0;i_s=0;t_a=4;t_c=2;t_l=1;t_s=0;o_d=1;o_c=1;r_c=0;tl=64"      --n_iters=100 --dataset_path="../data/exp_icl//datasets//real/minatar/name=Breakout-MinAtar//dataset.pkl"      --save_agent=False &> /Users/akarshkumar0101/cluster-run/temp_dir2/job_00041.log

touch /Users/akarshkumar0101/cluster-run/temp_dir2/job_00041.finish
