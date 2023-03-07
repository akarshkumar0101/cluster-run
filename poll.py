import re
import subprocess

import numpy as np

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