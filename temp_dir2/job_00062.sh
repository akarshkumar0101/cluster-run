#!/bin/bash
touch /Users/akarshkumar0101/cluster-run/temp_dir2/job_00062.start
echo $$ > /Users/akarshkumar0101/cluster-run/temp_dir2/job_00062.start

source /Users/akarshkumar0101/.virtualenvs/synthetic-mdps/bin/activate
cd /Users/akarshkumar0101/synthetic-mdps/src
python icl_bc.py --load_dir="../data/exp_icl//train_bc/all-name=SpaceInvaders-MinAtar"                                         --save_dir="../data/exp_icl//test_bc/name=SpaceInvaders-MinAtar/n-1"                                                                    --n_iters=100 --dataset_path="../data/exp_icl//datasets//real/minatar/name=SpaceInvaders-MinAtar//dataset.pkl" --save_agent=False &> /Users/akarshkumar0101/cluster-run/temp_dir2/job_00062.log

touch /Users/akarshkumar0101/cluster-run/temp_dir2/job_00062.finish
