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
from tqdm.auto import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("--command_file", type=str, default=None, help="filename to run")
parser.add_argument("--run_dir", type=str, default=None, help="location to run commands")
parser.add_argument("--experiment_dir", type=str, default=None)

parser.add_argument("--job_cpu_mem", type=int, default=0, help="cpu memory needed for each job (in MB)")
parser.add_argument("--job_gpu_mem", type=int, default=None, help="gpu memory needed for each job (in MB)")
parser.add_argument("--max_jobs_cpu", type=int, default=2, help="max number of jobs per cpu")
parser.add_argument("--max_jobs_gpu", type=int, default=10, help="max number of jobs per gpu")
parser.add_argument("--max_jobs_node", type=int, default=100, help="max number of jobs per computer node")

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

            for i_job, command in enumerate(tqdm(commands)):
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
    status_strs_unique = sorted(list(set(status_strs).union(set(status2str.values())).union({"unknown"})))
    nodes = np.array(["n/a" if job["node"] is None else job["node"] for job in metadata["jobs"]])
    nodes_unique = sorted(list(set(nodes).union({"n/a"})))

    d = np.zeros((len(nodes_unique), len(status_strs_unique)), dtype=object)
    for i_node, node in enumerate(nodes_unique):
        for i_status, status_str in enumerate(status_strs_unique):
            a = np.sum((nodes == node) & (status_strs == status_str))
            a = " " * 5 if a == 0 else f"{a: 5d}"
            d[i_node, i_status] = a
    df = pd.DataFrame(d, index=nodes_unique, columns=status_strs_unique)
    return tabulate(df, headers="keys", tablefmt="simple_grid")


class Server:
    def __init__(self, args):
        self.args = args
        self.metadata = None
        self.this_node = os.uname().nodename

        self.my_resources = self.get_server_resources()
        self.i_iter = 0
        self.popen2i_job = {}

    def get_server_resources(self):
        n_cpus = psutil.cpu_count()
        n_gpus = torch.cuda.device_count()
        mem_cpu = psutil.virtual_memory().available // 1000000
        mem_gpus = [torch.cuda.get_device_properties(i).total_memory // 1000000 for i in range(n_gpus)]

        if self.args.job_gpu_mem is not None:
            assert n_gpus > 0, "No GPUs found, and jobs require GPU memory."
        else:
            n_gpus = 1
            mem_gpus = [1000]
            self.args.job_gpu_mem = 0
            self.args.max_jobs_gpu = 10000

        self.args.mem_cpu = mem_cpu
        self.args.mem_gpus = mem_gpus

        # gpu mem/time bound
        n_procs_avail_per_gpu = [min(mem_gpu_i // self.args.job_gpu_mem if self.args.job_gpu_mem > 0 else np.inf, self.args.max_jobs_gpu) for mem_gpu_i in mem_gpus]
        # cpu mem/time bound
        n_procs_avail_cpu = min(mem_cpu // self.args.job_cpu_mem if self.args.job_cpu_mem > 0 else np.inf, self.args.max_jobs_cpu * n_cpus)
        # cpu/gpu bound
        n_procs = min(n_procs_avail_cpu, sum(n_procs_avail_per_gpu))
        n_procs = min(n_procs, self.args.max_jobs_node)
        n_procs_per_gpu = [0 for _ in n_procs_avail_per_gpu]
        i_gpu_ = 0
        for _ in range(n_procs):
            for i in range(len(n_procs_avail_per_gpu)):
                i_gpu = i_gpu_ % n_gpus
                i_gpu_ += 1
                if n_procs_per_gpu[i_gpu] < n_procs_avail_per_gpu[i_gpu]:
                    n_procs_per_gpu[i_gpu] += 1
                    break
        self.args.n_procs_per_gpu = n_procs_per_gpu
        return dict(n_procs_per_gpu=n_procs_per_gpu)

    def reserve_one_job(self, i_job, i_gpu):
        with open(f"{self.args.experiment_dir}/{i_job:010d}/run.sh", "w") as f:
            f.write("# !/bin/zsh\n")
            f.write(f"echo $HOME\n")
            f.write(f"source ~/.zshrc\n")
            f.write(f"source ~/activate_conda.sh\n")
            f.write(f"conda activate {self.args.conda_env}\n")
            f.write(f"cd {self.args.run_dir}\n")
            f.write(f"export CUDA_VISIBLE_DEVICES={self.metadata['jobs'][i_job]['gpu']}\n")
            f.write(f"{self.metadata['jobs'][i_job]['command']}\n")
        self.metadata["jobs"][i_job]["status"] = 1001
        self.metadata["jobs"][i_job]["status_str"] = status2str[1001]
        self.metadata["jobs"][i_job]["node"] = self.this_node
        self.metadata["jobs"][i_job]["gpu"] = i_gpu

    def reserve_jobs(self):
        # pending jobs
        idxs_jobs_pending = [i_job for i_job, job in enumerate(self.metadata["jobs"]) if job["status"] == 1000]

        n_procs_running = [0 for _ in self.my_resources["n_procs_per_gpu"]]
        running_popens = [popen for popen in self.popen2i_job.keys() if popen.poll() is None]
        for popen in running_popens:
            i_job = self.popen2i_job[popen]
            n_procs_running[self.metadata["jobs"][i_job]["gpu"]] += 1
        n_procs_avail = [a - b for a, b in zip(self.my_resources["n_procs_per_gpu"], n_procs_running)]
        n_procs_launched = [0 for _ in n_procs_avail]

        idxs_jobs = idxs_jobs_pending[: sum(n_procs_avail)]

        i_gpu_abs = 0
        for i_job in idxs_jobs:
            for i_gpu_abs in range(i_gpu_abs, i_gpu_abs + len(n_procs_avail)):
                i_gpu = i_gpu_abs % len(n_procs_avail)
                if n_procs_launched[i_gpu] < n_procs_avail[i_gpu]:
                    self.reserve_one_job(i_job, i_gpu)
                    n_procs_launched[i_gpu] += 1
                    break
        return idxs_jobs

    def launch_jobs(self, idxs_jobs):
        for i_job in idxs_jobs:
            job = self.metadata["jobs"][i_job]
            with open(f"{job['job_dir']}/out.txt", "w") as out_file, open(f"{job['job_dir']}/err.txt", "w") as err_file:
                # start_new_session=True is needed so SIGINT doesn't propagate to child processes
                popen = subprocess.Popen(f"zsh {job['job_dir']}/run.sh".split(" "), shell=False, start_new_session=True, stdout=out_file, stderr=err_file)
            self.metadata["jobs"][i_job]["pid"] = popen.pid
            self.popen2i_job[popen] = i_job

    def run_server(self):
        quitted = False
        start_time = datetime.now()
        while True:
            self.i_iter += 1
            try:
                time.sleep(2)
                print("\x1b[2J\x1b[H", end="")
                with filelock.FileLock(f"{self.args.experiment_dir}/metadata.json.lock"):
                    with open(f"{self.args.experiment_dir}/metadata.json", "r") as f:
                        self.metadata = json.load(f)

                    idxs_jobs = self.reserve_jobs() if not quitted else []
                    self.launch_jobs(idxs_jobs)
                    # if len(idxs_jobs) > 0:
                    # print(f"Launching {len(idxs_jobs)} jobs.")

                    popen2poll = {popen: popen.poll() for popen in self.popen2i_job}
                    popen2poll = {popen: (poll if poll is not None else 1002) for popen, poll in popen2poll.items()}
                    for popen, poll in popen2poll.items():
                        i_job = self.popen2i_job[popen]
                        job = self.metadata["jobs"][i_job]
                        job["status"] = poll
                        job["status_str"] = status2str[poll]
                        try:
                            job["pid_status"] = psutil.Process(job["pid"]).status()
                        except psutil.NoSuchProcess:
                            job["pid_status"] = "NoSuchProcess"

                    with open(f"{self.args.experiment_dir}/metadata.json", "w") as f:
                        json.dump(self.metadata, f, indent=4)

                    print(f"Running server!")
                    print(f"Node: {self.this_node}")
                    print(f"  Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"Iteration {self.i_iter: 10d}")
                    print("Args:")
                    print("-" * 80)
                    for k, v in vars(self.args).items():
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
                    print(get_status_txt_new(self.metadata))
                    # no_jobs_pending = all([job["status"] != 1000 for job in self.metadata["jobs"]])
                    # my_jobs_done = all([poll != 1002 for poll in popen2poll.values()])
                    # print(no_jobs_pending, my_jobs_done, [popen.poll() for popen in popen2poll])
                    # if no_jobs_pending and my_jobs_done:
                    #     break
                    should_wait = lambda status: status == 1002 or status == 1001 or (status == 1000 and not quitted)
                    if not any([should_wait(job["status"]) for job in self.metadata["jobs"]]):
                        break

            except KeyboardInterrupt:
                signal = input("Type signal to send to all jobs (ex. sigint=2, sigkill=9, sigterm=15): ")
                if signal.isdigit():
                    signal = int(signal)
                    print("Sending signal to all jobs: ", signal)
                    for popen in self.popen2i_job:
                        popen.send_signal(signal)
                    quitted = True
                else:
                    print("Did not understand signal. Continuing...")

        print("Done! Exiting Server")


def main(args):
    create_experiment(args)
    server = Server(args)
    server.run_server()


if __name__ == "__main__":
    main(parse_args())
