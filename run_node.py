
import argparse
import json
import os
import socket
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('dir_run', type=str, help='run directory')
parser.add_argument('--dir', type=str, default=None, help='location to run commands')
args = parser.parse_args()

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

print(f'Running on {hostname}: {command}')

idx_command = metadata['idx_command']
f_stdout = f'{args.dir_run}/{idx_command}/stdout.txt'
f_stderr = f'{args.dir_run}/{idx_command}/stderr.txt'
os.makedirs(os.path.dirname(f_stdout), exist_ok=True)
with open(f_stdout, 'wb') as out, open(f_stderr, 'wb') as err:
    p = subprocess.Popen(command, shell=True, start_new_session=True, stdout=out, stderr=err)
