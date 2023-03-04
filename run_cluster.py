
import argparse
import json
import os
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('filename', type=str, help='filename to run')
parser.add_argument('--dir', type=str, default=None, help='location to run commands')

parser.add_argument('--mem_gpu', type=int, default=5000, help='gpu memory needed for each job (in MB)')
parser.add_argument('--mem_cpu', type=int, default=5000, help='cpu memory needed for each job (in MB)')

args = parser.parse_args()

if args.dir is None:
    args.dir = os.getcwd()

print(args.dir)

with open(args.filename, 'r') as f:
    commands = f.readlines()
    commands = [line.strip() for line in commands]
    commands = [line for line in commands if len(line) > 0]

print(f'Found {len(commands)} commands in {args.filename}')
print()
print('First 5 commands: ')
for command in commands[:5]:
    print(command)
print('...')
print('')

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

print()

import time
from subprocess import run

while True:
    with open(f'{args.dir_run}/metadata.json', 'r') as f:
        metadata = json.load(f)
    if metadata['idx_command'] >= len(metadata['commands']):
        # no more commands to run
        break

    command = f'python run_node.py {args.dir_run} --dir {args.dir} --mem_gpu {args.mem_gpu} --mem_cpu {args.mem_cpu}'
    command = f'ssh visiongpu47.csail.mit.edu \"{command}\"'
    print(command)
    run(command, shell=True)
    time.sleep(.1)