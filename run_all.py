#!/usr/bin/env python3
"""Run the full pipeline: validation suite, then all four experiments.

    python run_all.py
"""

import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))

STEPS = [
    ("validation suite (34 checks)", ["tests/test_core.py"], ROOT),
    ("exp01  forward model", ["exp01_forward_model.py"], os.path.join(ROOT, "scripts")),
    ("exp02  inverse problem / ambiguity", ["exp02_inverse_ambiguity.py"], os.path.join(ROOT, "scripts")),
    ("exp03  precision: CRLB vs Monte Carlo", ["exp03_precision_crlb.py"], os.path.join(ROOT, "scripts")),
    ("exp04  systematic error budget", ["exp04_systematics.py"], os.path.join(ROOT, "scripts")),
]


def main():
    t_start = time.time()
    failures = []
    for label, args, cwd in STEPS:
        print()
        print("#" * 78)
        print(f"# {label}")
        print("#" * 78)
        t0 = time.time()
        r = subprocess.run([sys.executable] + args, cwd=cwd)
        dt = time.time() - t0
        status = "OK" if r.returncode == 0 else f"FAILED (exit {r.returncode})"
        print(f"\n# {label}: {status}  [{dt:.1f} s]")
        if r.returncode != 0:
            failures.append(label)

    print()
    print("=" * 78)
    print(f"  total wall time: {time.time() - t_start:.1f} s")
    if failures:
        print(f"  FAILURES: {failures}")
    else:
        print("  all steps completed; see results/ for figures and JSON output")
    print("=" * 78)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
