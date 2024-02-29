#!/bin/bash
touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_freeman-titanxp-1:0.start
echo $$ > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_freeman-titanxp-1:0.start

export CUDA_VISIBLE_DEVICES=0
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00000.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00012.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00024.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00036.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00048.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00060.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_freeman-titanxp-1:0.finish
