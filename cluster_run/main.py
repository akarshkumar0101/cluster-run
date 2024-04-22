import argparse
import json
import os
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--meta_dir", type=str, default=None, help="location to save metadata")
parser.add_argument("--force", type=lambda x: x.lower() == "true", default=False)

# job creation
parser.add_argument("--jobs_file", type=str, default=None, help="file with list of python jobs")
parser.add_argument("--venv", type=str, default=None, help="the virtual env to use")
parser.add_argument("--run_dir", type=str, default=None, help="location to run jobs")

# execution plan
parser.add_argument("--gpus_file", type=str, default=None, help="file with list of gpus")

# launch
parser.add_argument("--launch", type=lambda x: x.lower() == "true", default=False)


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


def create_experiment(args):
    print("Creating jobs...")

    # --------------------- Creating venv ---------------------
    if args.venv is None:
        args.venv = input("Enter venv: ")
    args.venv = os.path.abspath(os.path.expanduser(args.venv))
    # --------------------- Creating run_dir ---------------------
    if args.run_dir is None:
        args.run_dir = input("Enter run_dir: ")
    args.run_dir = os.path.abspath(os.path.expanduser(args.run_dir))

    # --------------------- Gathering jobs ---------------------
    if args.jobs_file is None:
        print("Enter the jobs.")
        jobs = get_multi_line_input()
    else:
        args.jobs_file = os.path.abspath(os.path.expanduser(args.jobs_file))
        with open(args.jobs_file) as f:
            jobs = f.read().split('\n')
    jobs = [job for job in jobs if job]
    job_ids = list(range(len(jobs)))
    print(f'Found {len(job_ids)} jobs.')
    with open(f"{args.meta_dir}/jobs.txt", "w") as f:
        f.write("\n".join(jobs))

    # --------------------- Gathering gpus ---------------------
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
    with open(f"{args.meta_dir}/nodes.txt", "w") as f:
        f.write("\n".join(nodes))
    with open(f"{args.meta_dir}/gpus.txt", "w") as f:
        f.write("\n".join(gpu_ids))

    print("Config: ")
    print(vars(args))
    with open(f"{args.meta_dir}/config.json", "w") as f:
        json.dump(vars(args), f, indent=4)

    # --------------------- Assigning jobs to gpus ---------------------
    print(f"Creating execution plan for {len(job_ids)} jobs over {len(gpu_ids)} gpus on {len(nodes)} nodes.")
    i_job_id, i_gpu_id = 0, 0
    job_id2gpu_id = {}
    while i_job_id < len(job_ids):
        gpu_id, job_id = gpu_ids[i_gpu_id], job_ids[i_job_id]
        job_id2gpu_id[job_id] = gpu_id
        i_job_id = i_job_id + 1
        i_gpu_id = (i_gpu_id + 1) % len(gpu_ids)
    gpu_id2job_ids = {gpu_id: [job_id for job_id in job_ids if job_id2gpu_id[job_id] == gpu_id] for gpu_id in gpu_ids}
    with open(f"{args.meta_dir}/gpu2jobs.json", "w") as f:
        json.dump(gpu_id2job_ids, f, indent=4)
    with open(f"{args.meta_dir}/job2gpu.json", "w") as f:
        json.dump(job_id2gpu_id, f, indent=4)

    # --------------------- Creating job_*.sh ---------------------
    header = f"source {args.venv}\ncd {args.run_dir}\n"
    for job_id, gpu_id in job_id2gpu_id.items():
        with open(f"{args.meta_dir}/job_{job_id:05d}.sh", "w") as f:
            f.write("#!/bin/bash\n")
            f.write("BASH_PID=$$\n")
            f.write(f"echo $BASH_PID > {args.meta_dir}/job_{job_id:05d}_bash.pid\n\n")  # write bash pid
            f.write(header)
            f.write(f"{jobs[job_id]} &> {args.meta_dir}/job_{job_id:05d}.log &\n\n")  # in background
            f.write("PYTHON_PID=$!\n")
            f.write(f"echo $PYTHON_PID > {args.meta_dir}/job_{job_id:05d}_python.pid\n")  # write python pid
            f.write(f"echo $PYTHON_PID >> {args.meta_dir}/gpu_{gpu_id}.pids\n")
            f.write("wait $PYTHON_PID\n")
            f.write("RETURN_CODE=$?\n")
            f.write(f"echo $RETURN_CODE > {args.meta_dir}/job_{job_id:05d}.return\n\n")  # write return code
    print("Done creating jobs.")

    # --------------------- Creating gpu_*.sh ---------------------
    for gpu_id in gpu_ids:
        node_id, cvd = gpu_id.split(":")
        with open(f"{args.meta_dir}/gpu_{gpu_id}.sh", "w") as f:
            f.write("#!/bin/bash\n")
            f.write("BASH_PID=$$\n")
            f.write(f"echo $BASH_PID > {args.meta_dir}/gpu_{gpu_id}_bash.pid\n")  # write pid to file
            f.write(f"echo $BASH_PID > {args.meta_dir}/gpu_{gpu_id}.pids\n\n")
            f.write(f"export CUDA_VISIBLE_DEVICES={cvd}\n")
            # f.write(f"export XLA_PYTHON_CLIENT_MEM_FRACTION=.95\n")
            for job_id in gpu_id2job_ids[gpu_id]:
                f.write(f"bash {args.meta_dir}/job_{job_id:05d}.sh\n")
            f.write("\n")
            f.write(f"touch {args.meta_dir}/gpu_{gpu_id}.finish\n")

    # --------------------- Creating launch.sh ---------------------
    with open(f"{args.meta_dir}/launch.sh", "w") as f:
        for gpu_id in gpu_ids:
            node_id, cvd = gpu_id.split(":")
            ssh_command = f"nohup bash {args.meta_dir}/gpu_{gpu_id}.sh >/dev/null 2>&1 </dev/null &"
            ssh_command = f"ssh {node_id}.csail.mit.edu \"hostname; {ssh_command}\""
            f.write(f"{ssh_command}\n")

    with open(f"{args.meta_dir}/pids.sh", "w") as f:
        for gpu_id in gpu_ids:
            node_id, cvd = gpu_id.split(":")
            ssh_command = f"$@ \\$(cat {args.meta_dir}/gpu_{gpu_id}.pids)"
            ssh_command = f"ssh {node_id}.csail.mit.edu \"hostname; {ssh_command}\""
            f.write(f"{ssh_command}\n")

    # with open(f"{args.meta_dir}/kill.sh", "w") as f:
    #     for gpu_id in gpu_ids:
    #         node_id, cvd = gpu_id.split(":")
    #         ssh_command = f"ps $(cat {args.meta_dir}/gpu_{gpu_id}.pids)"
    #         ssh_command = f"ssh {node_id}.csail.mit.edu \"hostname; {ssh_command}\""
    #         f.write(f"{ssh_command}\n")

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
    print("Some useful commands: ")
    print(f"cd {args.meta_dir}")
    print("bash launch.sh")
    print("bash pids.sh ps")
    print("bash pids.sh kill")
    # while True:
    #     a = input("Enter command: ")
    #     # print(a)
    #     # print(os.listdir(args.meta_dir))
    #     a = input()
    #     print(a)
    #     # take in lines as input jobs


def run_all(args):
    if args.meta_dir is None:
        now = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')  # current timestamp
        default_meta_dir = f"~/cluster_run_logs/{now}"
        print(f"Default meta_dir: {default_meta_dir}")
        args.meta_dir = input("Enter meta_dir (or press enter to use default): ")
        if not args.meta_dir:
            args.meta_dir = default_meta_dir
    args.meta_dir = os.path.abspath(os.path.expanduser(args.meta_dir))

    if args.force or not os.path.exists(args.meta_dir):
        print("Creating experiment...")
        os.system(f"rm -rf {args.meta_dir}")
        os.makedirs(args.meta_dir, exist_ok=True)
        create_experiment(args)
    else:
        print(f"Found existing experiment at {args.meta_dir}")

    if args.launch:
        launch_plan(args)

    run_dashboard(args)


def main():
    run_all(parse_args())


if __name__ == '__main__':
    main()
