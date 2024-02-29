#!/bin/bash
touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_torralba-titanv-1:0.start
echo $$ > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_torralba-titanv-1:0.start

export CUDA_VISIBLE_DEVICES=0
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00009.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00021.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00033.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00045.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00057.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_torralba-titanv-1:0.finish
