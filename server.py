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

parser.add_argument("--monitor", type=lambda x: x.lower() == "true", default=False)

parser.add_argument("--job_cpu_mem", type=int, default=0, help="cpu memory needed for each job (in MB)")
parser.add_argument("--job_gpu_mem", type=int, default=None, help="gpu memory needed for each job (in MB)")
parser.add_argument("--max_jobs_cpu", type=int, default=2, help="max number of jobs per cpu")
parser.add_argument("--max_jobs_gpu", type=int, default=10, help="max number of jobs per gpu")
parser.add_argument("--max_jobs_node", type=int, default=100, help="max number of jobs per computer node")
parser.add_argument("--conda_env", type=str, default=None, help="the conda environment to use")
parser.add_argument("--retry_crash", type=lambda x: x.lower() == "true", default=False, help="retry crashed runs")


# status2str = {1000: "pending", 1001: "reserved", 1002: "running", 0: "finished", 1: "crashed", -2: "siginted", -9: "sigkilled", -15: "sigtermed"}
# status2str = defaultdict(lambda: "unknown", status2str)


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
            metadata["job_data"] = {i_job: {} for i_job in range(len(commands))}
            metadata["node_data"] = {}

            for i_job, command in enumerate(tqdm(commands)):
                job_dir = f"{args.experiment_dir}/{int(i_job):010d}"
                os.makedirs(job_dir, exist_ok=True)
                metadata["job_data"][i_job] = {}
                metadata["job_data"][i_job]["command"] = command
                metadata["job_data"][i_job]["job_dir"] = job_dir
                metadata["job_data"][i_job]["status"] = "pending"
                metadata["job_data"][i_job]["node"] = "n/a"
                metadata["job_data"][i_job]["gpu"] = None
                metadata["job_data"][i_job]["pid"] = None
                metadata["job_data"][i_job]["pid_status"] = None
            with open(f"{args.experiment_dir}/metadata.json", "w") as f:
                json.dump(metadata, f, indent=4)
        else:
            print(f"Found existing experiment directory at {args.experiment_dir}")


def print_status_txt(metadata):
    nodes_unique = {job["node"] for i_job, job in metadata["job_data"].items()}
    status_unique = {job["status"] for i_job, job in metadata["job_data"].items()}
    nodes_unique = sorted(list(nodes_unique))
    status_unique = sorted(list(status_unique))

    df = np.zeros((len(nodes_unique), len(status_unique)), dtype=object)
    for i_node, node in enumerate(nodes_unique):
        for i_status, status in enumerate(status_unique):
            entry = np.sum([job["node"] == node and job["status"] == status for i_job, job in metadata["job_data"].items()])
            entry = " " * 5 if entry == 0 else f"{entry: 5d}"
            df[i_node, i_status] = entry

    def get_node_str(node):
        if node in metadata["node_data"]:
            last_update = metadata["node_data"][node]["last_update"]
            status = metadata["node_data"][node]["status"]
            return f"{node} ({status=}) ({last_update=})"
        else:
            return "?"

    nodes_unique = [get_node_str(node) for node in nodes_unique]
    df = pd.DataFrame(df, index=nodes_unique, columns=status_unique)
    print(tabulate(df, headers="keys", tablefmt="simple_grid"))


class Server:
    def __init__(self, args):
        self.args = args
        self.metadata = None
        self.this_node = os.uname().nodename

        self.resources = self.get_server_resources()  # n_procs_per_gpu ex. [3, 3, 3, 3]
        # self.used_resources = [0 for _ in self.resources]
        self.i_iter = 0
        self.popen2i_job = {}

    def get_server_resources(self):
        n_cpus = psutil.cpu_count()
        n_gpus = torch.cuda.device_count()
        mem_cpu = psutil.virtual_memory().available // 1000000
        mem_gpus = [torch.cuda.get_device_properties(i).total_memory // 1000000 for i in range(n_gpus)]

        if self.args.job_gpu_mem is not None:
            self.args.needs_gpus = True
            assert n_gpus > 0, "No GPUs found, and jobs require GPU memory."
        else:
            self.args.needs_gpus = False
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
        self.n_gpus = n_gpus
        return n_procs_per_gpu

    def reserve_one_job(self, i_job, i_gpu):
        job = self.metadata["job_data"][i_job]
        job["status"] = "reserved"
        job["node"] = self.this_node
        job["gpu"] = i_gpu
        with open(f"{self.args.experiment_dir}/{int(i_job):010d}/run.sh", "w") as f:
            f.write("# !/bin/zsh\n")
            f.write(f"echo $HOME\n")
            f.write(f"source ~/.zshrc\n")
            f.write(f"source ~/activate_conda.sh\n")
            f.write(f"conda activate {self.args.conda_env}\n")
            f.write(f"cd {self.args.run_dir}\n")
            f.write(f"export CUDA_VISIBLE_DEVICES={i_gpu}\n")
            f.write(f"{job['command']}\n")

    def reserve_jobs(self):
        # pending jobs
        idxs_jobs_pending = [i_job for i_job, job in self.metadata["job_data"].items() if job["status"] == "pending"]
        idxs_jobs_crashed = [i_job for i_job, job in self.metadata["job_data"].items() if job["status"] == "crashed"]
        idxs_jobs_to_take = idxs_jobs_pending + (idxs_jobs_crashed if self.args.retry_crash else [])

        n_procs_running = [0 for _ in self.resources]
        running_popens = [popen for popen in self.popen2i_job.keys() if popen.poll() is None]
        for popen in running_popens:
            i_job = self.popen2i_job[popen]
            n_procs_running[self.metadata["job_data"][i_job]["gpu"]] += 1
        n_procs_avail = [a - b for a, b in zip(self.resources, n_procs_running)]
        n_procs_launched = [0 for _ in n_procs_avail]

        idxs_jobs_reserved = idxs_jobs_to_take[: sum(n_procs_avail)]

        i_gpu_abs = 0
        for i_job in idxs_jobs_reserved:
            for i_gpu_abs in range(i_gpu_abs, i_gpu_abs + len(n_procs_avail)):
                i_gpu = i_gpu_abs % len(n_procs_avail)
                if n_procs_launched[i_gpu] < n_procs_avail[i_gpu]:
                    self.reserve_one_job(i_job, i_gpu)
                    n_procs_launched[i_gpu] += 1
                    break
        idxs_jobs_left = [i_job for i_job in idxs_jobs_to_take if i_job not in idxs_jobs_reserved]
        return idxs_jobs_reserved, idxs_jobs_left

    def launch_jobs(self, idxs_jobs):
        for i_job in idxs_jobs:
            job = self.metadata["job_data"][i_job]
            with open(f"{job['job_dir']}/out.txt", "w") as out_file, open(f"{job['job_dir']}/err.txt", "w") as err_file:
                # start_new_session=True is needed so SIGINT doesn't propagate to child processes
                popen = subprocess.Popen(f"zsh {job['job_dir']}/run.sh".split(" "), shell=False, start_new_session=True, stdout=out_file, stderr=err_file)
            self.metadata["job_data"][i_job]["pid"] = popen.pid
            self.popen2i_job[popen] = i_job
            print(f"Launching job: {i_job}")

    def test_gpus(self):
        out = subprocess.check_output("python gpu_check.py".split(" "), timeout=60)
        out = out.decode("utf-8")
        return "Success!" in out

    def update_metadata_jobs(self):
        n_jobs_running = 0
        for popen, i_job in self.popen2i_job.items():
            poll = popen.poll()
            poll2status = {None: "running", 0: "finished", 1: "crashed", -2: "siginted", -9: "sigkilled", -15: "sigtermed"}
            job = self.metadata["job_data"][i_job]
            job["status"] = poll2status[poll]
            if job["status"] == "running":
                n_jobs_running += 1
            try:
                job["pid_status"] = psutil.Process(job["pid"]).status()
            except psutil.NoSuchProcess:
                job["pid_status"] = "NoSuchProcess"
        return n_jobs_running

    def update_metadata_nodes(self, status=None):
        if self.this_node not in self.metadata["node_data"]:
            self.metadata["node_data"][self.this_node] = {}
        self.metadata["node_data"][self.this_node]["status"] = status
        self.metadata["node_data"][self.this_node]["start_time"] = self.start_time.strftime("%Y-%m-%d %H:%M:%S")
        self.metadata["node_data"][self.this_node]["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def run_server(self):
        self.start_time = datetime.now()
        while True:
            self.i_iter += 1
            try:
                if self.i_iter > 1:
                    time.sleep(10)
                self.test_gpus_result = self.test_gpus() if self.args.needs_gpus else True
                with filelock.FileLock(f"{self.args.experiment_dir}/metadata.json.lock"):
                    with open(f"{self.args.experiment_dir}/metadata.json", "r") as f:
                        self.metadata = json.load(f)

                    n_jobs_running = self.update_metadata_jobs()
                    self.update_metadata_nodes(status=self.test_gpus_result)

                    if self.test_gpus_result:
                        idxs_jobs_reserved, idxs_jobs_left = self.reserve_jobs()
                        self.launch_jobs(idxs_jobs_reserved)

                    n_jobs_running = self.update_metadata_jobs()
                    self.update_metadata_nodes(status=self.test_gpus_result)

                    with open(f"{self.args.experiment_dir}/metadata.json", "w") as f:
                        json.dump(self.metadata, f, indent=4)

                    if n_jobs_running == 0 and (len(idxs_jobs_left) == 0 or not self.test_gpus_result):
                        print("All jobs finished!")
                        break

            except KeyboardInterrupt:
                print("Interrupted")
                with filelock.FileLock(f"{self.args.experiment_dir}/metadata.json.lock"):
                    with open(f"{self.args.experiment_dir}/metadata.json", "r") as f:
                        self.metadata = json.load(f)
                    n_jobs_running = self.update_metadata_jobs()
                    self.update_metadata_nodes(status="interrupted")
                    with open(f"{self.args.experiment_dir}/metadata.json", "w") as f:
                        json.dump(self.metadata, f, indent=4)
                    # maybe kill all jobs?
                break
        print("Done! Exiting Server")

    def run_monitor(self):
        while True:
            time.sleep(5)
            with filelock.FileLock(f"{self.args.experiment_dir}/metadata.json.lock"):
                with open(f"{self.args.experiment_dir}/metadata.json", "r") as f:
                    self.metadata = json.load(f)
            print("\x1b[2J\x1b[H", end="")
            print_status_txt(self.metadata)


def main(args):
    print(args)
    create_experiment(args)
    server = Server(args)
    if args.monitor:
        server.run_monitor()
    else:
        server.run_server()


if __name__ == "__main__":
    main(parse_args())
