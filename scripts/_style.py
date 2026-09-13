"""Shared plotting setup and path helpers for the experiment scripts."""

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RESULTS = os.path.join(ROOT, "results")
sys.path.insert(0, ROOT)
os.makedirs(RESULTS, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 130,
    "savefig.dpi": 130,
    "savefig.bbox": "tight",
    "font.size": 9,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.6,
    "axes.axisbelow": True,
    "axes.titlesize": 10,
    "axes.titleweight": "bold",
    "legend.frameon": False,
    "legend.fontsize": 8,
    "lines.linewidth": 1.4,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "mathtext.default": "regular",
})

C = {
    "blue":   "#1f5fa8",
    "red":    "#c1382b",
    "green":  "#2e7d4f",
    "orange": "#d97a1a",
    "purple": "#6a4c93",
    "grey":   "#6b7280",
    "black":  "#1a1a1a",
}


def save(fig, name):
    fig.tight_layout()
    path = os.path.join(RESULTS, name)
    fig.savefig(path)
    plt.close(fig)
    print(f"    figure -> results/{name}")
    return path


def banner(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)
