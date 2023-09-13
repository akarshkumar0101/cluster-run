
for node in `cat nodes_all.txt | tail -n 1`
do
    ssh $node.csail.mit.edu "hostname; egb; which python; cd cluster-run; nohup python server.py --command_file=~/exploration-generalization/atari/experiments/goexplore/ge_finetune_ppo.sh --run_dir=~/exploration-generalization/atari --experiment_dir=~/experiments/ge_finetune_ppo/ --job_cpu_mem=1000 --job_gpu_mem=4000 --max_jobs_cpu=1 --max_jobs_gpu=3 --max_jobs_node=12 --conda_env=egb >/dev/null 2>&1 </dev/null &"
done