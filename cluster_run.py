import argparse

# import json
# import logging
import os
import re
import subprocess
import sys
from datetime import datetime

import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("filename", type=str, help="filename to run")
parser.add_argument("--dir", type=str, default=None, help="location to run commands")

parser.add_argument("--servers", nargs="*", type=str, default=None, help="either a list of servers or a file containing a list of servers")

parser.add_argument("--mem-gpu", type=int, default=5000, help="gpu memory needed for each job (in MB)")
parser.add_argument("--conda-env", type=str, default="base", help="the conda environment to use")

# parser.add_argument('--mem-cpu', type=int, default=5000, help='cpu memory needed for each job (in MB)')


def fetch_gpu_stats_server(server, timeout=10):
    # keys = ['total', 'reserved', 'used', 'free']
    keys = ["total", "used", "free"]
    commands = [f"nvidia-smi --query-gpu=memory.{key} --format=csv" for key in keys]
    command = " && echo ------- && ".join(commands)
    command = f'ssh {server} "{command}"'
    try:
        out = subprocess.check_output(command, shell=True, timeout=timeout).decode()
        data = {key: np.array(list(map(int, re.findall("\d+", o)))) for key, o in zip(keys, out.split("-------"))}
        return data
    except Exception as e:
        return None


def read_clean(file):
    with open(file, "r") as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if len(line) > 0]
    lines = [line for line in lines if line[0] != "#"]
    return lines


def main(args):
    if args.dir is None:
        args.dir = os.getcwd()

    args.cwd = os.getcwd()
    args.path_python = sys.executable

    now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dir_script = os.path.dirname(os.path.realpath(__file__))
    args.dir_cluster = f"{dir_script}/runs/{now_str}"

    os.makedirs(args.dir_cluster, exist_ok=True)
    print(f"Cluster directory: {args.dir_cluster}")

    print(args)

    commands = read_clean(args.filename)
    print("----------------------")
    print(f"Found {len(commands):05d} commands: ")
    print("\n".join(commands))

    if len(args.servers) == 1 and os.path.isfile(args.servers[0]):
        servers = read_clean(args.servers[0])
    else:
        servers = [f'{serv}.csail.mit.edu' for serv in args.servers]
    print("----------------------")
    print(f"Found {len(servers):05d} servers: ")
    print(" ".join(servers))

    servergpu2popens = dict()

    def launch_command(i_command, i_server, i_gpu):
        server_sh = []
        server_sh.append("#!/bin/zsh")
        server_sh.append(f"source ~/.zshrc")
        server_sh.append(f"source ~/activiate_conda.sh")
        server_sh.append(f"conda activate {args.conda_env}")
        server_sh.append(f"cd {args.dir}")
        # server_sh.append(f"alias python={args.path_python}")
        server_sh.append(f"export CUDA_VISIBLE_DEVICES={i_gpu}")
        server_sh.append(commands[i_command])  # ex. python train.py --lr 0.1
        server_sh = "\n".join(server_sh)

        f_run = f"{args.dir_cluster}/{i_command}/run.sh"
        f_stdout = f"{args.dir_cluster}/{i_command}/stdout.txt"
        f_stderr = f"{args.dir_cluster}/{i_command}/stderr.txt"
        os.makedirs(os.path.dirname(f_stdout), exist_ok=True)
        with open(f_run, "w") as f:
            f.write(server_sh)

        ssh_command = f'ssh {servers[i_server]} "zsh {f_run}"'
        print()
        print(f"{f_run}: ")
        print(server_sh)
        print()
        print(f"Launching command {i_command} on {servers[i_server]} GPU {i_gpu} with:")
        print(ssh_command)

        with open(f_stdout, "wb") as out, open(f_stderr, "wb") as err:
            popen = subprocess.Popen(ssh_command, shell=True, stdout=out, stderr=err, executable="zsh")
            servergpu2popens[(i_server, i_gpu)].append(popen)

    i_command = 0
    i_server = -1
    i_gpu = -1
    n_gpus = 0

    try:
        while i_command < len(commands):
            i_gpu += 1
            if i_gpu >= n_gpus:
                i_gpu = 0
                i_server = (i_server + 1) % len(servers)

            print("----------------------")
            print(f"Polling server {servers[i_server]} GPU {i_gpu}...")
            gpu_stats = fetch_gpu_stats_server(servers[i_server])
            n_gpus = len(gpu_stats["total"]) if gpu_stats is not None else 0

            if gpu_stats is None:
                print("Server not responding/other nvidia-smi error, skipping...")
                continue

            if (i_server, i_gpu) not in servergpu2popens:
                servergpu2popens[(i_server, i_gpu)] = []

            still_running = np.any([popen.poll() is None for popen in servergpu2popens[(i_server, i_gpu)]])
            if still_running:
                print("Server GPU still running previous commands, skipping...")
                continue

            print(f"Server GPU stats: {' '.join([f'{k}: {v[i_gpu]:06d} MB' for k, v in gpu_stats.items()])}")
            print(f"Required memory/command: {args.mem_gpu} MB")
            n_commands_this_gpu = gpu_stats["free"][i_gpu] // args.mem_gpu
            print(f"{gpu_stats['free'][i_gpu]}/{args.mem_gpu} -> {n_commands_this_gpu} commands.")

            for _ in range(n_commands_this_gpu):
                launch_command(i_command=i_command, i_server=i_server, i_gpu=i_gpu)
                i_command += 1
                if i_command >= len(commands):
                    break

        print("Done launching all commands! Waiting for them to finish...")
        for popens in servergpu2popens.values():
            for popen in popens:
                popen.wait()

    except KeyboardInterrupt:
        inp = input("Would you like to terminate or kill all processes? (t/k)")
        for (i_server, i_gpu), popens in servergpu2popens.items():
            for popen in popens:
                if popen.poll() is None:  # still running
                    print(f"{servers[i_server]} GPU {i_gpu} local PID: {popen.pid}")
                    if inp == "t":
                        popen.terminate()
                    elif inp == "k":
                        popen.kill()


if __name__ == "__main__":
    main(parser.parse_args())
