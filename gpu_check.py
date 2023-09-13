import torch
import subprocess

if __name__ == "__main__":
    # assert gpus are working
    out = subprocess.check_output("nvidia-smi")
    out = out.decode("utf-8")
    assert "NVIDIA-SMI" in out

    for i_gpu in range(torch.cuda.device_count()):
        print(f"Checking GPU {i_gpu}...")
        A = torch.randn(10, 10, device=f"cuda:{i_gpu}")
        B = torch.randn(10, 10, device=f"cuda:{i_gpu}")
        print((A @ B).mean().item())

    print("Success!")
