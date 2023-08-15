import subprocess

with open("servers_all.txt") as f:
    servers = [line.strip() for line in f.readlines()]
servers = [f"{server}.csail.mit.edu" for server in servers]
servers = servers

command = "nvidia-smi --query-gpu=timestamp,name,memory.total,memory.reserved,memory.used,memory.free --format=csv"
for server in servers:
    sshcommand = f"ssh -o 'StrictHostKeyChecking no' {server} '{command}'"
    print(server)
    try:
        out = subprocess.run(sshcommand, shell=True, capture_output=True, timeout=10)
    except:
        print("Timeout")
        continue
    print(out.stdout.decode())
    print()
