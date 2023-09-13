import argparse
import os
import socket
import time
from distutils.util import strtobool

import numpy as np
import torch

parser = argparse.ArgumentParser()
parser.add_argument("--device", type=str, default=None, help="device to run on")
parser.add_argument("--level", type=int, default=0, help="level")
parser.add_argument("--track", type=lambda x: bool(strtobool(x)), default=False, nargs="?", const=True)
parser.add_argument("--project", type=str, default="exploration-distillation")


def main(args):
    if args.device is None:
        args.device = "cuda" if torch.cuda.is_available() else "cpu"

    for i in range(60):
        print(i)
        time.sleep(1)
    print(f"{args=}")
    print(f"{os.uname().nodename=}")
    print(f"{os.getenv('CUDA_VISIBLE_DEVICES')=}")
    print(f"{torch.cuda.device_count()=}")
    for i in range(60):
        print(i)
        time.sleep(1)
    if np.random.random() < 0.5:
        raise Exception("Random exception")


if __name__ == "__main__":
    main(parser.parse_args())
