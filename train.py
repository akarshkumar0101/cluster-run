import argparse
import os
import socket
from distutils.util import strtobool

import torch

parser = argparse.ArgumentParser()
parser.add_argument("--device", type=str, default=None, help="device to run on")
parser.add_argument("--level", type=int, default=0, help='level')
parser.add_argument("--track", type=lambda x: bool(strtobool(x)), default=False, nargs="?", const=True)
parser.add_argument("--project", type=str, default='exploration-distillation')
args = parser.parse_args()

if args.device is None:
    args.device = 'cuda' if torch.cuda.is_available() else 'cpu'

hostname = socket.gethostname()
print(f'Hostname: {hostname}')
cvd = os.getenv('CUDA_VISIBLE_DEVICES')
print(f'Cuda visible devices: {cvd}')
print(f'Args: {args}')
