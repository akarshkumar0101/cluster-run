import argparse
import csv
import os
import subprocess
import time

parser = argparse.ArgumentParser()


def get_node_stats(node, timeout=5.):
    queries = 'count,gpu_name,memory.reserved,memory.total,memory.free,memory.used,utilization.gpu,utilization.memory'
    try:
        command = f'nvidia-smi --query-gpu={queries} --format=csv'
        command = f'ssh {node}.csail.mit.edu "{command}"'
        output = subprocess.check_output(command, timeout=timeout, shell=True, text=True).strip()

        def process_str(s):
            try:
                return int(s)
            except ValueError:
                pass
            if s.endswith(' MiB'):
                return int(s[:-4])
            if s.endswith(' %'):
                return int(s[:-2])
            return s

        reader = csv.reader(output.split('\n'), delimiter=',')
        data = [[process_str(val.strip()) for val in row] for row in reader]

        a = {}
        for i_gpu, row in enumerate(data[1:]):
            a[f"{node}:{i_gpu}"] = {}
            for key, val in zip(queries.split(','), row):
                a[f"{node}:{i_gpu}"][key] = val

        return a
    except Exception as e:
        print(f"Error in get_node_stats({node}):")
        print(e)
        return None


def print_it(data):
    s = []
    for gpu, d in data.items():
        mem_use, mem_total = d['memory.used'], d['memory.total']
        util_gpu, util_mem = d['utilization.gpu'], d['utilization.memory']
        n = 20
        a = int((mem_use / mem_total) * n)
        b = int(util_gpu / 100 * n)
        c = int(util_mem / 100 * n)

        s_mem = f"mem: {'=' * a}{'.' * (n - a)} {mem_use:6d}/{mem_total:6d} MB"
        s_util_gpu = f"gpu_util: {'=' * b}{'.' * (n - b)} {util_gpu:3d}%"
        s_util_mem = f"mem_util: {'=' * c}{'.' * (n - c)} {util_mem:3d}%"
        # s.append(f"{gpu:20s}  {s_mem}  {s_util_gpu}  {s_util_mem}")
        s.append(f"{gpu:20s}  {s_mem}  {s_util_gpu}")

    for i, si in enumerate(s):
        print(si, end="\n" if i % 2 == 1 else " | ")


def main():
    with open("./nodes_all1.txt", "r") as f:
        nodes = f.read().split('\n')
        nodes = [node for node in nodes if node]
    print(nodes)

    data = {}
    i_node = 0
    while True:
        try:
            node = nodes[i_node]
            i_node = (i_node + 1) % len(nodes)

            data_node = get_node_stats(node)
            if data_node is not None:
                data.update(data_node)

            print("\x1b[2J\x1b[H", end="")
            os.system('clear')

            print_it(data)
            time.sleep(1.)
        except KeyboardInterrupt:
            gpus = []
            for gpu, d in data.items():
                if d['memory.used'] / d['memory.total'] < .1 and d['utilization.gpu'] < .1:
                    gpus.append(gpu)

            print("\x1b[2J\x1b[H", end="")
            os.system('clear')
            print(f"------ Free GPUs: {len(gpus)} ------")
            for i, gpu in enumerate(gpus):
                print(gpu)
            time.sleep(10)


if __name__ == "__main__":
    main()
