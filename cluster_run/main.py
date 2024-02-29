import argparse
import json
import os
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--meta_dir", type=str, default=None, help="location to save metadata")

# job creation
parser.add_argument("--jobs_file", type=str, default=None, help="file with list of python jobs")
parser.add_argument("--venv", type=str, default=None, help="the virtual env to use")
parser.add_argument("--run_dir", type=str, default=None, help="location to run jobs")

# execution plan
parser.add_argument("--gpus_file", type=str, default=None, help="file with list of gpus")

# launch
parser.add_argument("--launch", type=lambda x: x.lower() == "true", default=None)


def parse_args(*args, **kwargs):
    args = parser.parse_args(*args, **kwargs)
    return args


def get_multi_line_input():
    print("Enter/Paste your content. Enter 'done' to finish.")
    lines = []
    while True:
        line = input()
        if line == 'done':  # not using EOF because it closes stdin
            break
        lines.append(line)
    print(f'Closing with {len(lines)} lines.')
    return lines


def create_jobs(args):
    print("Creating jobs...")
    if args.venv is None:
        args.venv = input("Enter venv: ")
    args.venv = os.path.abspath(os.path.expanduser(args.venv))
    if args.run_dir is None:
        args.run_dir = input("Enter run_dir: ")
    args.run_dir = os.path.abspath(os.path.expanduser(args.run_dir))
    if args.jobs_file is None:
        print("Enter the jobs.")
        jobs = get_multi_line_input()
    else:
        args.jobs_file = os.path.abspath(os.path.expanduser(args.jobs_file))
        with open(args.jobs_file) as f:
            jobs = f.read().split('\n')
    jobs = [job for job in jobs if job]
    job_ids = list(range(len(jobs)))

    print("Config: ")
    print(vars(args))
    os.system(f"rm -rf {args.meta_dir}")
    os.makedirs(args.meta_dir, exist_ok=True)
    with open(f"{args.meta_dir}/config.json", "w") as f:
        json.dump(vars(args), f, indent=4)

    print(f'Found {len(job_ids)} jobs.')

    with open(f"{args.meta_dir}/jobs.txt", "w") as f:
        f.write("\n".join(jobs))

    header = f"source {args.venv}\ncd {args.run_dir}\n"
    for job_id in job_ids:
        with open(f"{args.meta_dir}/job_{job_id:05d}.sh", "w") as f:
            f.write("#!/bin/bash\n")
            f.write(f"touch {args.meta_dir}/job_{job_id:05d}.start\n")
            f.write(f"echo $$ > {args.meta_dir}/job_{job_id:05d}.start\n\n")
            f.write(header)
            f.write(f"{jobs[job_id]} &> {args.meta_dir}/job_{job_id:05d}.log\n\n")
            f.write(f"touch {args.meta_dir}/job_{job_id:05d}.finish\n")

    print("Done creating jobs.")


def create_execution_plan(args):
    print("Creating execution plan...")

    if args.gpus_file is None:
        print("Enter the gpus.")
        lines = get_multi_line_input()
    else:
        args.gpus_file = os.path.abspath(os.path.expanduser(args.gpus_file))
        with open(args.gpus_file) as f:
            lines = f.read().split('\n')
    lines = [line for line in lines if line]

    nodes, gpu_ids = [], []
    for line in lines:
        node, gpus_desc = line.split(":")
        if ',' in gpus_desc:
            gpus = [int(i) for i in gpus_desc.split(",")]
        elif '..' in gpus_desc:
            start, end = gpus_desc.split("..")
            gpus = list(range(int(start), int(end) + 1))
        else:
            gpus = [int(gpus_desc)]

        for gpu in gpus:
            gpu_ids.append(f"{node}:{gpu}")
        nodes.append(node)
    nodes, gpu_ids = sorted(set(nodes)), sorted(set(gpu_ids))

    print(f'Found {len(nodes)} nodes: {nodes}')
    print(f'Found {len(gpu_ids)} gpus: {gpu_ids}')

    with open(f"{args.meta_dir}/jobs.txt", "r") as f:
        jobs = f.read().split('\n')
    job_ids = list(range(len(jobs)))

    print(f"Creating execution plan for {len(job_ids)} jobs over {len(gpu_ids)} gpus on {len(nodes)} nodes.")

    i_job_id, i_gpu_id = 0, 0
    gpu_id2job_ids = {gpu_id: [] for gpu_id in gpu_ids}
    while i_job_id < len(job_ids):
        gpu_id, job_id = gpu_ids[i_gpu_id], job_ids[i_job_id]
        gpu_id2job_ids[gpu_id].append(job_id)
        i_job_id = i_job_id + 1
        i_gpu_id = (i_gpu_id + 1) % len(gpu_ids)

    with open(f"{args.meta_dir}/assignments.json", "w") as f:
        json.dump(gpu_id2job_ids, f, indent=4)

    for gpu_id in gpu_ids:
        node_id, gpu = gpu_id.split(":")
        with open(f"{args.meta_dir}/gpu_{node_id}:{gpu}.sh", "w") as f:
            f.write("#!/bin/bash\n")
            f.write(f"touch {args.meta_dir}/gpu_{node_id}:{gpu}.start\n")
            f.write(f"echo $$ > {args.meta_dir}/gpu_{node_id}:{gpu}.start\n\n")
            f.write(f"export CUDA_VISIBLE_DEVICES={gpu}\n")
            for job_id in gpu_id2job_ids[gpu_id]:
                f.write(f"bash {args.meta_dir}/{job_id:05d}.sh\n")
            f.write("\n")
            f.write(f"touch {args.meta_dir}/gpu_{node_id}:{gpu}.finish\n")

    with open(f"{args.meta_dir}/launch.sh", "w") as f:
        for gpu_id in gpu_ids:
            node_id, gpu = gpu_id.split(":")
            ssh_command = f"nohup bash {args.meta_dir}/gpu_{node_id}:{gpu}.sh >/dev/null 2>&1 </dev/null &"
            ssh_command = f"ssh {node_id}.csail.mit.edu \"hostname; {ssh_command}\""
            f.write(f"{ssh_command}\n")

    # with open(f"{args.meta_dir}/check_gpu.sh", "w") as f:
    #     for node in nodes:
    #         ssh_command = f"ssh {node}.csail.mit.edu \"hostname; nvidia-smi\""
    #         f.write(f"{ssh_command}\n")
    # print(args.meta_dir)

    print("Done creating execution plan.")


def launch_plan(args):
    print("Launching execution plan...")
    # os.system(f"bash {args.meta_dir}/launch.sh")


def run_dashboard(args):
    print("Running dashboard...")
    print(args.meta_dir)
    while True:
        a = input("Enter command: ")
        # print(a)
        # print(os.listdir(args.meta_dir))
        a = input()
        print(a)
        # take in lines as input jobs


def run_all(args):
    if args.meta_dir is None:
        now = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')  # current timestamp
        default_meta_dir = f"~/cluster_run_logs/{now}"
        print(f"Default meta_dir: {default_meta_dir}")
        args.meta_dir = input("Enter meta_dir (or press enter to use default): ")
        if not args.meta_dir:
            args.meta_dir = default_meta_dir
    args.meta_dir = os.path.abspath(os.path.expanduser(args.meta_dir))

    if not os.path.exists(args.meta_dir):
        create_jobs(args)
    else:
        yn = input(f"Found existing experiment at {args.meta_dir}, use this? (y/n): ")
        if yn.lower() == "n":
            create_jobs(args)

    if not os.path.exists(f"{args.meta_dir}/launch.sh"):
        create_execution_plan(args)
    else:
        yn = input(f"Found existing execution plan at {args.meta_dir}, use this? (y/n): ")
        if yn.lower() == "n":
            create_execution_plan(args)

    if args.launch is None:
        yn = input(f"Launch plan? (y/n): ")
        args.launch = yn.lower() == "y"
    if args.launch:
        launch_plan(args)

    run_dashboard(args)


def main():
    run_all(parse_args())


if __name__ == '__main__':
    main()
