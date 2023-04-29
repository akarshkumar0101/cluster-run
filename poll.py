import argparse
# import json
# import logging
import os

import numpy as np

from cluster_run import fetch_gpu_stats_server, read_clean

parser = argparse.ArgumentParser()
parser.add_argument('--servers', nargs='*', type=str, default=None,
                    help='either a list of servers or a file containing a list of servers')
parser.add_argument('--mem-gpu', type=int, default=5000, help='gpu memory needed for each job (in MB)')


# parser.add_argument('--mem-cpu', type=int, default=5000, help='cpu memory needed for each job (in MB)')

def main(args):
    print(args)

    servers = args.servers
    if len(args.servers) == 1 and os.path.isfile(args.servers[0]):
        servers = read_clean(args.servers[0])
    print('----------------------')
    print(f'Found {len(servers):05d} servers: ')
    print(' '.join(servers))

    n_commands = 0
    for server in servers:
        print('----------------------')
        print(f'Polling server {server}...')
        gpu_stats = fetch_gpu_stats_server(server)
        if gpu_stats is None:
            print('Server not responding/other nvidia-smi error, skipping...')
            continue

        print([f'{f}/{t}' for f, t in zip(gpu_stats['free'], gpu_stats['total'])])
        n_commands += np.sum(gpu_stats['free'] // args.mem_gpu)
        print(f"   GPU possible jobs: {gpu_stats['free'] // args.mem_gpu}")
        print(f"Server possible jobs: {np.sum(gpu_stats['free'] // args.mem_gpu)}")

        # print(f"Server GPU stats: {' '.join([f'{k}: {v[i_gpu]:06d} MB' for k, v in gpu_stats.items()])}")
        print(f"Required memory/command: {args.mem_gpu} MB")
        # n_commands_this_gpu = gpu_stats['free'][i_gpu]//args.mem_gpu
        # print(f"{gpu_stats['free'][i_gpu]}/{args.mem_gpu} -> {n_commands_this_gpu} commands.")
    print('----------------------')
    print(f'Total possible jobs: {n_commands}')


if __name__ == '__main__':
    main(parser.parse_args())
