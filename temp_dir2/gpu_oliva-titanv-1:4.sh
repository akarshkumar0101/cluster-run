#!/bin/bash
touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:4.start
echo $$ > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:4.start

export CUDA_VISIBLE_DEVICES=4
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00005.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00017.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00029.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00041.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00053.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:4.finish
