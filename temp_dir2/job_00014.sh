#!/bin/bash
touch /Users/akarshkumar0101/cluster-run/temp_dir2/job_00014.start
echo $$ > /Users/akarshkumar0101/cluster-run/temp_dir2/job_00014.start

source /Users/akarshkumar0101/.virtualenvs/synthetic-mdps/bin/activate
cd /Users/akarshkumar0101/synthetic-mdps/src
python icl_bc.py --load_dir="../data/exp_icl//train_bc/all-name=Acrobot-v1"                                                    --save_dir="../data/exp_icl//test_bc/name=Acrobot-v1/n-1"                                                                               --n_iters=100 --dataset_path="../data/exp_icl//datasets//real/classic/name=Acrobot-v1//dataset.pkl"            --save_agent=False &> /Users/akarshkumar0101/cluster-run/temp_dir2/job_00014.log

touch /Users/akarshkumar0101/cluster-run/temp_dir2/job_00014.finish
