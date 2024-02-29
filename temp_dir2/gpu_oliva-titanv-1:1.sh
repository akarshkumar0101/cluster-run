#!/bin/bash
touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:1.start
echo $$ > /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:1.start

export CUDA_VISIBLE_DEVICES=1
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00002.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00014.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00026.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00038.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00050.sh
bash /Users/akarshkumar0101/cluster-run/temp_dir2/00062.sh

touch /Users/akarshkumar0101/cluster-run/temp_dir2/gpu_oliva-titanv-1:1.finish
