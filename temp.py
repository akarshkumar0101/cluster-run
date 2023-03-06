import re
import subprocess

import numpy as np


def get_gpu_stats_server(server, timeout=5):
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

n_gpus = 0
for i in range(44, 54):
    print(f'visiongpu{i}:')
    try:
        stats = get_gpu_stats_server(f'visiongpu{i}.csail.mit.edu')
        print(stats['free'])
        print(stats['free']/5000)
        n_gpus += (stats['free']//5000).astype(int).sum()
    except Exception as e:
        print(e)
print(n_gpus)
