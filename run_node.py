
import argparse
import json
import os
import socket
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument('dir_run', type=str, help='run directory')
parser.add_argument('--dir', type=str, default=None, help='location to run commands')

parser.add_argument('--mem_gpu', type=int, default=5000, help='gpu memory needed for each job (in MB)')
parser.add_argument('--mem_cpu', type=int, default=5000, help='cpu memory needed for each job (in MB)')

args = parser.parse_args()

cwd = os.getcwd()
path_python = sys.executable

hostname = socket.gethostname()

with open(f'{args.dir_run}/metadata.json', 'r') as f:
    metadata = json.load(f)
if metadata['idx_command'] >= len(metadata['commands']):
    # exit program
    print('No more commands to run')
    exit(0)

command = metadata['commands'][metadata['idx_command']]

metadata['idx_command'] += 1
metadata['command2hostname'][command] = hostname
with open(f'{args.dir_run}/metadata.json', 'w') as f:
    json.dump(metadata, f)

print(f'Launching on {hostname}: {command} at location {args.dir}')

command = f'cd {args.dir} && alias python={path_python} && {command}'

idx_command = metadata['idx_command']
f_stdout = f'{args.dir_run}/{idx_command}/stdout.txt'
f_stderr = f'{args.dir_run}/{idx_command}/stderr.txt'
os.makedirs(os.path.dirname(f_stdout), exist_ok=True)
with open(f_stdout, 'wb') as out, open(f_stderr, 'wb') as err:
    p = subprocess.Popen(command, shell=True, start_new_session=True, stdout=out, stderr=err)
