#!/bin/bash
touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:7.start
echo $$ > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:7.start

export CUDA_VISIBLE_DEVICES=7
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00008.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00020.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00032.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00044.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00056.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:7.finish
