#!/bin/bash
touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:5.start
echo $$ > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:5.start

export CUDA_VISIBLE_DEVICES=5
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00006.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00018.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00030.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00042.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00054.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:5.finish
