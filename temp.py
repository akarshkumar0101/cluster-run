import re
import subprocess

import numpy as np


def get_gpu_stats_server(server, timeout=10):
    # keys = ['total', 'reserved', 'used', 'free']
    keys = ['total', 'used', 'free']
    commands = [f'nvidia-smi --query-gpu=memory.{key} --format=csv' for key in keys]
    command = ' && echo ------- && '.join(commands)
    
    command = f'ssh {server} \"{command}\"'
    # proc = run(command, shell=True, capture_output=True)
    # out = proc.stdout.decode()
    out = subprocess.check_output(command, shell=True, timeout=timeout).decode()
    data = {key: np.array(list(map(int, re.findall('\d+', o))))
            for key, o in zip(keys, out.split('-------'))}
    return data


# read in servers_isolab.txt
with open('servers_isolab.txt', 'r') as f:
    servers = f.readlines()
    servers = [line.strip() for line in servers]
    servers = [line for line in servers if len(line) > 0]
    servers = [line for line in servers if line[0] != '#']

n_gpus = 0
for server in servers:
    print()
    print('-----------')
    print(server)
    try:
        stats = get_gpu_stats_server(server)
        print(stats['free'])
        print(stats['free']/5000)
        n_gpus += (stats['free']//5000).astype(int).sum()
    except Exception as e:
        print(e)
print(n_gpus)
