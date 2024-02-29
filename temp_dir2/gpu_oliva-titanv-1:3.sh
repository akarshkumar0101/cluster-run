#!/bin/bash
touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:3.start
echo $$ > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:3.start

export CUDA_VISIBLE_DEVICES=3
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00004.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00016.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00028.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00040.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00052.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:3.finish
