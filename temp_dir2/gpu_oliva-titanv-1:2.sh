#!/bin/bash
touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:2.start
echo $$ > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:2.start

export CUDA_VISIBLE_DEVICES=2
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00003.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00015.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00027.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00039.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00051.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00063.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:2.finish
