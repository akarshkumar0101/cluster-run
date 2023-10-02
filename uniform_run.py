import argparse
import os
import sys
import shutil
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--commands_file", type=str, default=None, help="file with list of commands")
parser.add_argument("--nodes_file", type=str, default=None, help="file with list of nodes")
parser.add_argument("--run_dir", type=str, default=None, help="location to run commands")
parser.add_argument("--exp_dir", type=str, default=None)
parser.add_argument("--conda_env", type=str, default=None, help="the conda environment to use")

# parser.add_argument("--job_cpu_mem", type=int, default=0, help="cpu memory needed for each job (in MB)")
# parser.add_argument("--job_gpu_mem", type=int, default=None, help="gpu memory needed for each job (in MB)")
# parser.add_argument("--max_jobs_cpu", type=int, default=2, help="max number of jobs per cpu")
# parser.add_argument("--max_jobs_gpu", type=int, default=10, help="max number of jobs per gpu")
# parser.add_argument("--max_jobs_node", type=int, default=100, help="max number of jobs per computer node")

parser.add_argument("--launch", type=lambda x: x.lower() == "true", default=False)


def parse_args(*args, **kwargs):
    args = parser.parse_args(*args, **kwargs)
    args.commands_file = os.path.abspath(os.path.expanduser(args.commands_file))
    args.nodes_file = os.path.abspath(os.path.expanduser(args.nodes_file))
    args.run_dir = os.path.abspath(os.path.expanduser(args.run_dir))
    args.exp_dir = os.path.abspath(os.path.expanduser(args.exp_dir))
    args.cwd = os.getcwd()
    args.executable = sys.executable
    return args


def main(args):
    os.makedirs(args.exp_dir, exist_ok=True)
    os.makedirs(f"{args.exp_dir}/job_logs", exist_ok=True)
    os.makedirs(f"{args.exp_dir}/node_logs", exist_ok=True)
    shutil.copyfile(args.commands_file, f"{args.exp_dir}/commands.sh")

    with open(args.commands_file) as f:
        commands = [line for line in f.read().split('\n') if line]
    jobs = [dict(id=i, command=command) for i, command in enumerate(commands)]
    print(f'Found {len(jobs)} jobs.')

    with open(args.nodes_file) as f:
        nodes = [line for line in f.read().split('\n') if line]
    print(f'Found {len(nodes)} nodes.')

    node2jobs = {node: [] for node in nodes}
    for job in jobs:
        node = nodes[job['id'] % len(nodes)]
        node2jobs[node].append(job)

    for node in nodes:
        print(f'{node: >30s}: {len(node2jobs[node]): >7d} jobs')

    node2lines = {node: [] for node in nodes}
    for node, jobs in node2jobs.items():
        node2lines[node].append('#!/bin/zsh')
        node2lines[node].append('echo \"$HOME\"')
        node2lines[node].append('source ~/activate_conda.sh')
        node2lines[node].append(f'conda activate {args.conda_env}')
        node2lines[node].append(f'cd {args.run_dir}')
        node2lines[node].append('')

        for i_job, job in enumerate(jobs):
            job_id, command = job['id'], job['command']
            command = f'CUDA_VISIBLE_DEVICES={i_job % 4} {command} &> {args.exp_dir}/job_logs/{job_id}.log &'
            node2lines[node].append(command)
            if (i_job + 1) % 4 == 0:
                node2lines[node].append('echo \"launched 4 jobs\"')
                node2lines[node].append('wait')

    for node, lines in node2lines.items():
        with open(f'{args.exp_dir}/{node}.sh', 'w') as f:
            f.write('\n'.join(lines))
    print('Done writing node scripts.')

    if args.launch:
        print('Launching nodes...')
        for node in nodes:
            ssh_command = f"zsh {args.exp_dir}/{node}.sh"
            ssh_command = f"nohup {ssh_command} &> {args.exp_dir}/node_logs/{node}.log &"
            ssh_command = f"ssh {node}.csail.mit.edu \"{ssh_command}\""
            print(ssh_command)
            subprocess.run(ssh_command, shell=True)
            print('Done!')


if __name__ == '__main__':
    main(parse_args())
