#!/bin/bash
touch /Users/akarshkumar0101/cluster-run/temp_dir2/job_00023.start
echo $$ > /Users/akarshkumar0101/cluster-run/temp_dir2/job_00023.start

source /Users/akarshkumar0101/.virtualenvs/synthetic-mdps/bin/activate
cd /Users/akarshkumar0101/synthetic-mdps/src
python icl_bc.py --load_dir=None                                                                                               --save_dir="../data/exp_icl//test_bc/name=MountainCar-v0/scratch"                                                                       --n_iters=100 --dataset_path="../data/exp_icl//datasets//real/classic/name=MountainCar-v0//dataset.pkl"        --save_agent=False &> /Users/akarshkumar0101/cluster-run/temp_dir2/job_00023.log

touch /Users/akarshkumar0101/cluster-run/temp_dir2/job_00023.finish
