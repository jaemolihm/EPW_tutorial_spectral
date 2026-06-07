#!/usr/bin/env python3
"""Generate kpt_near_K.txt sampling along Gamma-K between alpha1*K and alpha2*K,
where K = [1/3, 1/3, 0] in crystal coordinates.

Usage: ./generate_k.py alpha1 alpha2 [N]
       (N defaults to 100)
"""
import sys
import numpy as np


def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: ./generate_k.py alpha1 alpha2 [N]")
    alpha1 = float(sys.argv[1])
    alpha2 = float(sys.argv[2])
    N = int(sys.argv[3]) if len(sys.argv) > 3 else 100

    K = np.array([1.0 / 3.0, 1.0 / 3.0, 0.0])
    alphas = np.linspace(alpha1, alpha2, N)
    pts = np.outer(alphas, K)

    with open("kpt_near_K.txt", "w") as f:
        f.write(f"{N} crystal\n")
        for p in pts:
            f.write(f"    {p[0]:.6f}    {p[1]:.6f}    {p[2]:.6f}   1.0\n")
    print(f"Wrote {N} k-points (alpha = {alpha1} -> {alpha2}) to kpt_near_K.txt")


if __name__ == "__main__":
    main()
