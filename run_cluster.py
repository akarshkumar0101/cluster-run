
# Akarsh
import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime

import numpy as np

# from subprocess import run

parser = argparse.ArgumentParser()
parser.add_argument('filename', type=str, help='filename to run')
parser.add_argument('--dir', type=str, default=None, help='location to run commands')

parser.add_argument('--mem_gpu', type=int, default=5000, help='gpu memory needed for each job (in MB)')
# parser.add_argument('--mem_cpu', type=int, default=5000, help='cpu memory needed for each job (in MB)')

args = parser.parse_args()

if args.dir is None:
    args.dir = os.getcwd()

cwd = os.getcwd()
path_python = sys.executable
print(f'{cwd=}')
print(f'{path_python=}')
print(f'{args.dir=}')
print()

with open(args.filename, 'r') as f:
    commands = f.readlines()
    commands = [line.strip() for line in commands]
    commands = [line for line in commands if len(line) > 0]
    commands = [line for line in commands if line[0] != '#']

print(f'Found {len(commands)} commands in {args.filename}, First 3: ')
for command in commands[:3]:
    print(command)
print('...')
print()

now = datetime.now()
# dir_run = now.strftime('%Y-%m-%d_%H-%M-%S')
dir_run = now.strftime('%Y-%m-%d_%H')
dir_script = os.path.dirname(os.path.realpath(__file__))
dir_run = f'{dir_script}/runs/{dir_run}'
args.dir_run = dir_run

print(f'Creating run directory: {args.dir_run}')
os.makedirs(args.dir_run, exist_ok=True)

with open(f'{args.dir_run}/commands.txt', 'w') as f:
    f.write('\n'.join(commands))

metadata = dict(commands=commands, idx_command=0, command2hostname=dict())
with open(f'{args.dir_run}/metadata.json', 'w') as f:
    json.dump(metadata, f)


with open(f'{dir_script}/servers.txt', 'r') as f:
    servers = f.readlines()
    servers = [line.strip() for line in servers]

print(f'Found {len(servers)} servers, First 3: ')
for server in servers[:3]:
    print(server)
print('...')
print()


def get_gpu_stats_server(server):
    # keys = ['total', 'reserved', 'used', 'free']
    keys = ['total', 'used', 'free']
    commands = [f'nvidia-smi --query-gpu=memory.{key} --format=csv' for key in keys]
    command = ' && echo ------- && '.join(commands)
    
    command = f'ssh {server} \"{command}\"'
    # proc = run(command, shell=True, capture_output=True)
    # out = proc.stdout.decode()
    out = subprocess.check_output(command, shell=True).decode()
    data = {key: np.array(list(map(int, re.findall('\d+', o))))
            for key, o in zip(keys, out.split('-------'))}
    return data

# for server in servers:
#     print(server)
#     print(get_mem_server(server)['free'])

servergpu2popens = dict()

def launch_command(idx_command, idx_server, idx_gpu):
    command = commands[idx_command]

    command = f'cd {args.dir} && alias python={path_python} && {command}'
    command = f'export CUDA_VISIBLE_DEVICES={idx_gpu} && {command}'
    if idx_server is not None:
        command = f'ssh {servers[idx_server]} \"{command}\"'

    print(f'Launching command {idx_command} on {servers[idx_server]}, GPU {idx_gpu} with:')
    print(command)
    print()

    f_stdout = f'{args.dir_run}/{idx_command}/stdout.txt'
    f_stderr = f'{args.dir_run}/{idx_command}/stderr.txt'
    os.makedirs(os.path.dirname(f_stdout), exist_ok=True)
    with open(f_stdout, 'wb') as out, open(f_stderr, 'wb') as err:
        popen = subprocess.Popen(command, shell=True, stdout=out, stderr=err, executable='zsh')
        servergpu2popens[(idx_server, idx_gpu)].append(popen)

idx_command = 0
idx_server = 0
idx_gpu = 0
while idx_command < len(commands):
    if (idx_server, idx_gpu) not in servergpu2popens:
        servergpu2popens[(idx_server, idx_gpu)] = []
    
    gpu_stats = get_gpu_stats_server(servers[idx_server])
    n_gpus = len(gpu_stats['total'])

    n_commands_this_gpu = gpu_stats['free'][idx_gpu]//args.mem_gpu
    print(gpu_stats['free'][idx_gpu], args.mem_gpu)
    print(n_commands_this_gpu)
    print()

    done_running = np.all([popen.poll() is not None for popen in servergpu2popens[(idx_server, idx_gpu)]])
    if done_running:
        for _ in range(n_commands_this_gpu):
            launch_command(idx_command=idx_command, idx_server=idx_server, idx_gpu=idx_gpu)
            idx_command += 1
            if idx_command >= len(commands):
                break

    idx_gpu += 1
    if idx_gpu>=n_gpus:
        idx_gpu = 0
        idx_server = (idx_server+1)%len(servers)

for popens in servergpu2popens.values():
    for popen in popens:
        popen.wait()
