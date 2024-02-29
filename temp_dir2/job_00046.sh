#!/bin/bash
touch /Users/akarshkumar0101/cluster-run/temp_dir2/job_00046.start
echo $$ > /Users/akarshkumar0101/cluster-run/temp_dir2/job_00046.start

source /Users/akarshkumar0101/.virtualenvs/synthetic-mdps/bin/activate
cd /Users/akarshkumar0101/synthetic-mdps/src
python icl_bc.py --load_dir="../data/exp_icl//train_bc/all-name=Breakout-MinAtar"                                              --save_dir="../data/exp_icl//test_bc/name=Breakout-MinAtar/n-1"                                                                         --n_iters=100 --dataset_path="../data/exp_icl//datasets//real/minatar/name=Breakout-MinAtar//dataset.pkl"      --save_agent=False &> /Users/akarshkumar0101/cluster-run/temp_dir2/job_00046.log

touch /Users/akarshkumar0101/cluster-run/temp_dir2/job_00046.finish
