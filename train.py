import argparse
from distutils.util import strtobool

parser = argparse.ArgumentParser()
parser.add_argument("--device", type=str, default='cpu', help="device to run on")
parser.add_argument("--level", type=int, default=0, help='level')
parser.add_argument("--track", type=lambda x: bool(strtobool(x)), default=False, nargs="?", const=True)
parser.add_argument("--project", type=str, default='exploration-distillation')
args = parser.parse_args()

print(f'RUNNING: {args}')



