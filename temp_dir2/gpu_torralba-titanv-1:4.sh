#!/bin/bash
touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_torralba-titanv-1:4.start
echo $$ > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_torralba-titanv-1:4.start

export CUDA_VISIBLE_DEVICES=4
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00011.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00023.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00035.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00047.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00059.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_torralba-titanv-1:4.finish
