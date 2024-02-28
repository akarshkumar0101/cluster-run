import argparse
import json
import os
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--meta_dir", type=str, default=None, help="location to save metadata")

parser.add_argument("--jobs_file", type=str, default=None, help="file with list of python jobs")
parser.add_argument("--gpus_file", type=str, default=None, help="file with list of gpus")

parser.add_argument("--venv", type=str, default=None, help="the virtual env to use")
parser.add_argument("--run_dir", type=str, default=None, help="location to run jobs")

parser.add_argument("--launch", type=lambda x: x.lower() == "true", default=False)


def parse_args(*args, **kwargs):
    args = parser.parse_args(*args, **kwargs)
    args.jobs_file = os.path.abspath(os.path.expanduser(args.jobs_file))
    args.run_dir = os.path.abspath(os.path.expanduser(args.run_dir))
    args.venv = os.path.abspath(os.path.expanduser(args.venv))

    if args.meta_dir is None:
        # current timestamp
        now = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        args.meta_dir = f"~/cluster_run_logs/{now}"
    args.meta_dir = os.path.abspath(os.path.expanduser(args.meta_dir))
    # args.cwd = os.getcwd()
    # args.executable = sys.executable
    return args


def create_experiment(args):
    print("Creating experiment with config: ")
    print(vars(args))
    return None
    os.system(f"rm -rf {args.meta_dir}")
    os.makedirs(args.meta_dir, exist_ok=True)

    with open(f"{args.meta_dir}/config.json", "w") as f:
        json.dump(vars(args), f, indent=4)

    with open(args.jobs_file) as f:
        jobs = [line for line in f.read().split('\n') if line]
    job_ids = list(range(len(jobs)))

    # with open(args.nodes) as f:
    #     nodes = [line for line in f.read().split('\n') if line]
    nodes = ['t1', 't2', 't3', 't4']
    nodes2n_gpus = {'t1': 4, 't2': 4, 't3': 3, 't4': 4}

    print(f'Found {len(jobs)} jobs.')
    print(f'Found {len(nodes)} nodes.')

    with open(f"{args.meta_dir}/jobs.sh", "w") as f:
        f.write("\n".join(jobs))

    i_job, i_node = 0, 0
    node2blocks = {node: [] for node in nodes}
    while i_job < len(jobs):
        node = nodes[i_node]
        n_gpus = nodes2n_gpus[node]
        i_node = (i_node + 1) % len(nodes)
        node2blocks[node].append(job_ids[i_job:i_job + n_gpus])
        i_job += n_gpus

    with open(f"{args.meta_dir}/assignments.json", "w") as f:
        json.dump(node2blocks, f, indent=4)

    header = "\n".join(["#!/bin/bash",
                        f"source {args.venv}",
                        f"cd {args.run_dir}"])
    for node in nodes:
        with open(f"{args.meta_dir}/{node}.sh", "w") as f:
            f.write(header)
            f.write("\n\n")
            # write the bash script's PID to a file
            f.write(f"echo $$ > {args.meta_dir}/{node}.pid\n")
            f.write(f"touch {args.meta_dir}/{node}.start\n")
            f.write("\n")
            for block in node2blocks[node]:
                for i_gpu, i_job in enumerate(block):
                    cvd = f"CUDA_VISIBLE_DEVICES={i_gpu}"
                    write_log = f"&> {args.meta_dir}/{i_job:05d}.log"
                    start_indicator = f"touch {args.meta_dir}/{i_job:05d}.start"
                    finish_indicator = f"touch {args.meta_dir}/{i_job:05d}.finish"
                    f.write(f"({start_indicator} && {cvd} {jobs[i_job]} {write_log} && {finish_indicator}) &\n")
                f.write("wait\n")
            f.write("\n")
            f.write(f"touch {args.meta_dir}/{node}.finish\n")

    with open(f"{args.meta_dir}/launch.sh", "w") as f:
        for node in nodes:
            ssh_command = f"nohup bash {args.meta_dir}/{node}.sh >/dev/null 2>&1 </dev/null &"
            ssh_command = f"ssh {node}.csail.mit.edu \"hostname; {ssh_command}\""
            f.write(f"{ssh_command}\n")

    with open(f"{args.meta_dir}/check_gpu.sh", "w") as f:
        for node in nodes:
            ssh_command = f"ssh {node}.csail.mit.edu \"hostname; nvidia-smi\""
            f.write(f"{ssh_command}\n")
    print(args.meta_dir)


def manage_experiment(args):
    while True:
        # a = input("Enter command: ")
        # print(a)
        # print(os.listdir(args.meta_dir))
        a = input()
        print(a)
        # take in lines as input jobs


def main(args):
    # check if meta_dir exists
    if not os.path.exists(args.meta_dir):
        create_experiment(args)
    else:
        print(f"Directory {args.meta_dir} already exists.")
    manage_experiment(args)


if __name__ == '__main__':
    main(parse_args())
