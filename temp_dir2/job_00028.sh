#!/bin/bash
touch /Users/akarshkumar0101/cluster-run/temp_dir2/job_00028.start
echo $$ > /Users/akarshkumar0101/cluster-run/temp_dir2/job_00028.start

source /Users/akarshkumar0101/.virtualenvs/synthetic-mdps/bin/activate
cd /Users/akarshkumar0101/synthetic-mdps/src
python icl_bc.py --load_dir="../data/exp_icl//train_bc/name=DiscretePendulum-v1"                                               --save_dir="../data/exp_icl//test_bc/name=DiscretePendulum-v1/name=DiscretePendulum-v1"                                                 --n_iters=100 --dataset_path="../data/exp_icl//datasets//real/classic/name=DiscretePendulum-v1//dataset.pkl"   --save_agent=False &> /Users/akarshkumar0101/cluster-run/temp_dir2/job_00028.log

touch /Users/akarshkumar0101/cluster-run/temp_dir2/job_00028.finish
