#!/bin/bash
touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:6.start
echo $$ > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:6.start

export CUDA_VISIBLE_DEVICES=6
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00007.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00019.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00031.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00043.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00055.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:6.finish
