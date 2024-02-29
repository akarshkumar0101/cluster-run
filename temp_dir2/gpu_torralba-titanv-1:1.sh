#!/bin/bash
touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_torralba-titanv-1:1.start
echo $$ > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_torralba-titanv-1:1.start

export CUDA_VISIBLE_DEVICES=1
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00010.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00022.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00034.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00046.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00058.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_torralba-titanv-1:1.finish
