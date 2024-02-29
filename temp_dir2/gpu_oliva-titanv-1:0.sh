#!/bin/bash
touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:0.start
echo $$ > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:0.start

export CUDA_VISIBLE_DEVICES=0
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00001.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00013.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00025.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00037.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00049.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00061.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:0.finish
