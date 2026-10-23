"""
QuantumShield - Visual Assets Generator
Generates high-resolution PNG charts:
- assets/qber_comparison.png
- assets/monte_carlo_distribution.png
- assets/circuit_diagram.png
"""

import os
import matplotlib.pyplot as plt
import numpy as np

from src.simulation import run_bb84_simulation, run_repeated_experiments
from src.visualization import (
    plot_qber_comparison,
    plot_repeated_trials,
    setup_dark_style,
    NAVY_BG,
    PANEL_BG,
    CYAN_ACCENT,
    VIOLET_ACCENT,
    TEXT_COLOR,
)


def generate_all_visuals():
    os.makedirs("assets", exist_ok=True)

    # 1. QBER Comparison Benchmark
    res_no = run_bb84_simulation(n_qubits=200, eve_present=False, noise_rate=0.0, seed=42)
    res_with = run_bb84_simulation(n_qubits=200, eve_present=True, noise_rate=0.0, seed=99)
    fig_comp = plot_qber_comparison(res_no, res_with, threshold=5.0)
    fig_comp.savefig("assets/qber_comparison.png", dpi=200, bbox_inches="tight", facecolor=NAVY_BG)
    plt.close(fig_comp)
    print("Saved assets/qber_comparison.png")

    # 2. Monte Carlo Variance
    mc_data = run_repeated_experiments(n_trials=10, n_qubits_per_trial=100, eve_present=True, base_seed=123)
    fig_mc = plot_repeated_trials(mc_data)
    fig_mc.savefig("assets/monte_carlo_distribution.png", dpi=200, bbox_inches="tight", facecolor=NAVY_BG)
    plt.close(fig_mc)
    print("Saved assets/monte_carlo_distribution.png")

    # 3. Quantum Circuit Visual Diagram
    fig, ax = plt.subplots(figsize=(10, 3.5), facecolor=NAVY_BG)
    setup_dark_style(ax)
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.5)

    # Wire
    ax.plot([0.5, 9.5], [1.8, 1.8], color="#64748b", lw=2, zorder=1)
    ax.text(0.3, 1.8, "q[0]", color=TEXT_COLOR, va="center", ha="right", fontsize=12, fontweight="bold", family="monospace")

    # Gate drawer helper
    def draw_gate(x, y, label, sublabel, color, border):
        box = plt.Rectangle((x-0.45, y-0.45), 0.9, 0.9, facecolor=color, edgecolor=border, lw=2, zorder=3)
        ax.add_patch(box)
        ax.text(x, y+0.1, label, color="#ffffff", ha="center", va="center", fontsize=11, fontweight="bold", family="sans-serif", zorder=4)
        ax.text(x, y-0.22, sublabel, color="#cbd5e1", ha="center", va="center", fontsize=7.5, family="sans-serif", zorder=4)

    # Barrier drawer
    def draw_barrier(x):
        ax.plot([x, x], [0.8, 2.8], color="#94a3b8", linestyle="--", lw=1.5, zorder=2)

    # 1. Alice Gates
    draw_gate(1.5, 1.8, "X", "Alice Prep", "#0284c7", CYAN_ACCENT)
    draw_gate(2.6, 1.8, "H", "Diagonal", "#0284c7", CYAN_ACCENT)
    draw_barrier(3.3)
    ax.text(3.3, 3.0, "Channel Barrier", color="#94a3b8", fontsize=8, ha="center", style="italic")

    # 2. Eve Gates
    draw_gate(4.2, 1.8, "M", "Eve Intercept", "#991b1b", "#ef4444")
    draw_gate(5.3, 1.8, "X", "Eve Resend", "#991b1b", "#ef4444")
    draw_barrier(6.0)

    # 3. Bob Gates
    draw_gate(6.9, 1.8, "H", "Bob Basis", "#7c3aed", VIOLET_ACCENT)
    draw_gate(8.0, 1.8, "M", "Measurement", "#7c3aed", VIOLET_ACCENT)

    # Title
    ax.text(5.0, 3.25, "Representative Qiskit BB84 Single-Qubit Transmission Circuit", color=TEXT_COLOR, fontsize=13, fontweight="bold", ha="center")

    fig.savefig("assets/circuit_diagram.png", dpi=200, bbox_inches="tight", facecolor=NAVY_BG)
    plt.close(fig)
    print("Saved assets/circuit_diagram.png")


if __name__ == "__main__":
    generate_all_visuals()
