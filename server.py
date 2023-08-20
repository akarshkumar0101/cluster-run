import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime

import filelock
import numpy as np
import pandas as pd
import psutil
import torch
from tabulate import tabulate

parser = argparse.ArgumentParser()
parser.add_argument("--command_file", type=str, default=None, help="filename to run")
parser.add_argument("--run_dir", type=str, default=None, help="location to run commands")
parser.add_argument("--experiment_dir", type=str, default=None)

parser.add_argument("--mem_gpu", type=int, default=1000, help="gpu memory needed for each job (in MB)")
parser.add_argument("--mem_cpu", type=int, default=1000, help="cpu memory needed for each job (in MB)")
parser.add_argument("--max_jobs_gpu", type=int, default=10, help="max number of jobs per gpu")
parser.add_argument("--max_jobs_cpu", type=int, default=2, help="max number of jobs per cpu")

parser.add_argument("--conda_env", type=str, default=None, help="the conda environment to use")

status2str = {1000: "pending", 1001: "reserved", 1002: "running", 0: "finished", 1: "crashed", -2: "siginted", -9: "sigkilled", -15: "sigtermed"}
status2str = defaultdict(lambda: "unknown", status2str)


def parse_args(*args, **kwargs):
    args = parser.parse_args(*args, **kwargs)
    args.command_file = os.path.abspath(os.path.expanduser(args.command_file))
    args.run_dir = os.path.abspath(os.path.expanduser(args.run_dir))
    args.experiment_dir = os.path.abspath(os.path.expanduser(args.experiment_dir))

    args.cwd = os.getcwd()
    args.executable = sys.executable
    return args


def read_clean(file):
    with open(file, "r") as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if len(line) > 0]
    lines = [line for line in lines if line[0] != "#"]
    return lines


def create_experiment(args):
    os.makedirs(args.experiment_dir, exist_ok=True)

    with filelock.FileLock(f"{args.experiment_dir}/metadata.json.lock"):
        if not os.path.exists(f"{args.experiment_dir}/metadata.json"):
            print(f"Creating new experiment directory at {args.experiment_dir}")
            commands = read_clean(args.command_file)
            print(f"Found {len(commands):10d} commands.")
            with open(f"{args.experiment_dir}/commands.txt", "w") as f:
                f.write("\n".join(commands))

            metadata = {}
            metadata["args"] = vars(args)
            metadata["jobs"] = [{} for _ in range(len(commands))]

            for i_job, command in enumerate(commands):
                job_dir = f"{args.experiment_dir}/{i_job:010d}"
                os.makedirs(job_dir, exist_ok=True)
                metadata["jobs"][i_job] = {}
                metadata["jobs"][i_job]["command"] = command
                metadata["jobs"][i_job]["job_dir"] = job_dir
                metadata["jobs"][i_job]["status"] = 1000
                metadata["jobs"][i_job]["status_str"] = status2str[1000]
                metadata["jobs"][i_job]["node"] = None
                metadata["jobs"][i_job]["pid"] = None
                metadata["jobs"][i_job]["pid_status"] = None
                metadata["jobs"][i_job]["gpu"] = None
                with open(f"{args.experiment_dir}/metadata.json", "w") as f:
                    json.dump(metadata, f, indent=4)
        else:
            print(f"Found existing experiment directory at {args.experiment_dir}")


# def get_status_txt(metadata, idxs_jobs=None):
#     if idxs_jobs is None:
#         idxs_jobs = list(range(len(metadata["jobs"])))
#     status_txt = []
#     status_txt.append("-" * 80)
#     status_str2count = Counter([job["status_str"] for job in metadata["jobs"]])
#     for status_str in list(status2str.values()) + ["unknown"]:
#         count = status_str2count[status_str]
#         status_txt.append(f"{status_str:>10s}: {count:> 10d}       ({count/len(idxs_jobs)*100 if len(idxs_jobs)>0 else 0:5.1f}%)")
#     status_txt.append(". " * 40)
#     status_txt.append(f"{'total':>10s}: {len(idxs_jobs):10d}       ({100 if len(idxs_jobs)>0 else 0:5.1f}%)")
#     status_txt.append("-" * 80)
#     status_txt.append("")
#     return "\n".join(status_txt)


def get_status_txt_new(metadata):
    status_strs = np.array([job["status_str"] for job in metadata["jobs"]])
    # status2str = {1000: "pending", 1001: "reserved", 1002: "running", 0: "finished", 1: "crashed", -2: "siginted", -9: "sigkilled", -15: "sigtermed"}
    status_strs_unique = sorted(list(set(status_strs).union(set(status2str.values()))))
    nodes = np.array(["n/a" if job["node"] is None else job["node"] for job in metadata["jobs"]])
    nodes_unique = sorted(list(set(nodes).union({"n/a"})))

    d = np.zeros((len(nodes_unique), len(status_strs_unique)), dtype=object)
    for i_node, node in enumerate(nodes_unique):
        for i_status, status_str in enumerate(status_strs_unique):
            d[i_node, i_status] = np.sum((nodes == node) & (status_strs == status_str))
            if d[i_node, i_status] == 0:
                d[i_node, i_status] = ""
    df = pd.DataFrame(d, index=nodes_unique, columns=status_strs_unique)
    return tabulate(df, headers="keys", tablefmt="psql")


class Server:
    def __init__(self, args):
        self.args = args
        self.get_server_resources()

        self.i_iter = 0
        self.popen2i_job = {}

    def get_server_resources(self):
        args = self.args
        n_cpus = psutil.cpu_count()
        n_gpus = torch.cuda.device_count()
        mem_cpu = psutil.virtual_memory().available // 1000000
        mem_gpus = [torch.cuda.get_device_properties(i).total_memory // 1000000 for i in range(n_gpus)]
        mem_gpus = [3000, 6000]

        # gpu mem/time bound
        n_procs_avail_per_gpu = [min(mem_gpu_i // args.mem_gpu, args.max_jobs_gpu) for mem_gpu_i in mem_gpus]
        # cpu mem/time bound
        n_procs_avail_cpu = min(mem_cpu // args.mem_cpu, args.max_jobs_cpu * n_cpus)
        # cpu/gpu bound
        n_procs = min(n_procs_avail_cpu, sum(n_procs_avail_per_gpu))
        n_procs_per_gpu = [0 for _ in n_procs_avail_per_gpu]
        for _ in range(n_procs):
            for i_gpu in range(len(n_procs_avail_per_gpu)):
                if n_procs_per_gpu[i_gpu] < n_procs_avail_per_gpu[i_gpu]:
                    n_procs_per_gpu[i_gpu] += 1
        self.n_procs_per_gpu = n_procs_per_gpu

    def reserve_jobs(self):
        idxs_jobs = []
        idxs_jobs = [i_job for i_job, job in enumerate(metadata["jobs"]) if job["status"] == 1000]
        idxs_jobs = idxs_jobs[:3]

        for i_job in idxs_jobs:
            with open(f"{args.experiment_dir}/{i_job:010d}/run.sh", "w") as f:
                f.write("# !/bin/zsh\n")
                f.write(f"echo $HOME\n")
                f.write(f"source ~/.zshrc\n")
                # f.write(f"source ~/activate_conda.sh\n")
                f.write(f"conda activate {args.conda_env}\n")
                f.write(f"cd {args.run_dir}\n")
                f.write(f"export CUDA_VISIBLE_DEVICES={metadata['jobs'][i_job]['gpu']}\n")
                f.write(f"{metadata['jobs'][i_job]['command']}\n")
            metadata["jobs"][i_job]["status"] = 1001
            metadata["jobs"][i_job]["node"] = os.uname().nodename
        return idxs_jobs

    def write_jobs(args):
        pass

    def launch_jobs(self, idxs_jobs):
        for i_job in idxs_jobs:
            job = metadata["jobs"][i_job]
            with open(f"{job['job_dir']}/out.txt", "w") as out_file, open(f"{job['job_dir']}/err.txt", "w") as err_file:
                # start_new_session=True is needed so SIGINT doesn't propagate to child processes
                popen = subprocess.Popen(f"zsh {job['job_dir']}/run.sh".split(" "), shell=False, start_new_session=True, stdout=out_file, stderr=err_file)
            metadata["jobs"][i_job]["pid"] = popen.pid
            popen2i_job[popen] = i_job

    def run_server(args):
        this_node = os.uname().nodename
        i_iter = 0
        while True:
            i_iter += 1
            try:
                time.sleep(1)
                with filelock.FileLock(f"{args.experiment_dir}/metadata.json.lock"):
                    with open(f"{args.experiment_dir}/metadata.json", "r") as f:
                        metadata = json.load(f)

                    # print("\r" * len(status_str.split("\n")), end="")

                    popen2poll = {popen: popen.poll() for popen in popen2i_job}
                    popen2poll = {popen: (poll if poll is not None else 1002) for popen, poll in popen2poll.items()}

                    idxs_jobs = reserve_jobs(args, metadata)
                    launch_jobs(args, metadata, idxs_jobs, popen2i_job)
                    if len(idxs_jobs) > 0:
                        print(f"Launching {len(idxs_jobs)} jobs.")

                    for popen, poll in popen2poll.items():
                        i_job = popen2i_job[popen]
                        job = metadata["jobs"][i_job]
                        job["status"] = poll
                        job["status_str"] = status2str[poll]
                        try:
                            job["pid_status"] = psutil.Process(job["pid"]).status()
                        except psutil.NoSuchProcess:
                            job["pid_status"] = "NoSuchProcess"

                    with open(f"{args.experiment_dir}/metadata.json", "w") as f:
                        json.dump(metadata, f, indent=4)

                    print("\x1b[2J\x1b[H", end="")
                    print(f"Running server!")
                    print(f"Node: {this_node}")
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"Iteration {i_iter:010d}")
                    print("Args:")
                    print("-" * 80)
                    for k, v in vars(args).items():
                        print(f"{k:20s}: {v}")
                    print("-" * 80)
                    print()

                    # all_nodes = [job["node"] for job in metadata["jobs"] if job["node"] is not None]
                    # all_nodes = list(set(all_nodes))
                    # print("All nodes: ", " ".join(all_nodes))
                    # print(get_status_txt(metadata))
                    # print(f"This node: {this_node}")
                    # idxs_jobs = [i_job for i_job, job in enumerate(metadata["jobs"]) if job["node"] == this_node]
                    # print(get_status_txt(metadata, idxs_jobs))
                    # print([metadata["jobs"][i_job]["pid_status"] for i_job in idxs_jobs])
                    print(get_status_txt_new(metadata))

                    no_jobs_pending = all([job["status"] != 1000 for job in metadata["jobs"]])
                    my_jobs_done = all([poll != 1002 for poll in popen2poll.values()])
                    if no_jobs_pending and my_jobs_done:
                        break

            except KeyboardInterrupt:
                signal = input("Type signal to send to all jobs (ex. sigint=2, sigkill=9, sigterm=15): ")
                signal = int(signal)
                print("Sending signal to all jobs: ", signal)
                for popen in popen2i_job:
                    popen.send_signal(signal)

        print("Done! Exiting Server")


def main(args):
    create_experiment(args)
    run_server(args)


if __name__ == "__main__":
    main(parse_args())
