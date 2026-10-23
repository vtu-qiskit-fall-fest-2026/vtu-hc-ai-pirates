"""
QuantumShield - Visualization Module
Renders Matplotlib charts for QBER comparisons, basis matching distributions,
Monte Carlo trial distributions, and noise sweeps.
"""

from typing import Optional, List, Dict, Any
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from src.protocol import ProtocolResult


# Configure dark navy hackathon styling
matplotlib.use("Agg")
NAVY_BG = "#0b1120"
PANEL_BG = "#111c38"
CYAN_ACCENT = "#06b6d4"
VIOLET_ACCENT = "#a855f7"
TEXT_COLOR = "#e2e8f0"
GREEN_COLOR = "#10b981"
RED_COLOR = "#ef4444"


def setup_dark_style(ax: plt.Axes) -> None:
    """Applies QuantumShield dark navy theme to matplotlib axis."""
    ax.set_facecolor(PANEL_BG)
    ax.tick_params(colors=TEXT_COLOR, labelsize=10)
    for spine in ax.spines.values():
        spine.set_color("#334155")
        spine.set_linewidth(1.2)
    ax.grid(True, color="#1e293b", linestyle="--", alpha=0.7)


def plot_qber_comparison(
    result_no_eve: Optional[ProtocolResult],
    result_with_eve: Optional[ProtocolResult],
    threshold: float = 5.0,
) -> plt.Figure:
    """
    Creates a comparative bar chart showing observed QBER vs theoretical expectations
    for both Eve-disabled and Eve-enabled scenarios.
    """
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor=NAVY_BG)
    setup_dark_style(ax)

    categories = []
    observed_qber = []
    theoretical_qber = []

    if result_no_eve is not None:
        categories.append("Without Eve\n(Direct Channel)")
        observed_qber.append(result_no_eve.qber * 100.0)
        theoretical_qber.append(0.0)

    if result_with_eve is not None:
        categories.append("With Eve\n(Intercept-Resend)")
        observed_qber.append(result_with_eve.qber * 100.0)
        theoretical_qber.append(25.0)

    x = np.arange(len(categories))
    width = 0.35

    if len(categories) > 0:
        bars_obs = ax.bar(x - width/2, observed_qber, width, label="Observed QBER (%)", color=CYAN_ACCENT, edgecolor="#38bdf8", linewidth=1.5)
        bars_theo = ax.bar(x + width/2, theoretical_qber, width, label="Theoretical QBER (%)", color=VIOLET_ACCENT, alpha=0.7, edgecolor="#c084fc", linewidth=1.5, hatch="//")

        for bar in bars_obs:
            height = bar.get_height()
            ax.annotate(f"{height:.1f}%",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 4), textcoords="offset points",
                        ha="center", va="bottom", color=TEXT_COLOR, fontweight="bold", fontsize=10)

        for bar in bars_theo:
            height = bar.get_height()
            ax.annotate(f"{height:.1f}%",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 4), textcoords="offset points",
                        ha="center", va="bottom", color="#cbd5e1", fontsize=9)

        ax.set_xticks(x)
        ax.set_xticklabels(categories, color=TEXT_COLOR, fontweight="bold", fontsize=11)

    # Configurable warning threshold line
    ax.axhline(threshold, color="#f59e0b", linestyle=":", linewidth=2, label=f"Warning Threshold ({threshold:.1f}%)")
    ax.axhline(11.0, color="#ef4444", linestyle="--", linewidth=1.5, alpha=0.7, label="Shor-Preskill Limit (11%)")

    ax.set_ylabel("Error Rate (%)", color=TEXT_COLOR, fontsize=11)
    ax.set_title("Quantum Bit Error Rate (QBER) Benchmark", color=TEXT_COLOR, fontsize=14, fontweight="bold", pad=12)
    ax.set_ylim(0, max(35.0, max(observed_qber + [30.0]) + 5))
    ax.legend(facecolor=PANEL_BG, edgecolor="#334155", labelcolor=TEXT_COLOR, fontsize=9, loc="upper left")

    plt.tight_layout()
    return fig


def plot_cumulative_error_rate(result: ProtocolResult) -> plt.Figure:
    """
    Plots the convergence of QBER across transmissions as sifted bits accumulate.
    """
    fig, ax = plt.subplots(figsize=(8, 4), facecolor=NAVY_BG)
    setup_dark_style(ax)

    running_errors = 0
    running_sifted = 0
    sifted_steps = []
    error_rates = []

    for tx in result.transmissions:
        if tx.basis_matched:
            running_sifted += 1
            if not tx.bit_matched:
                running_errors += 1
            sifted_steps.append(running_sifted)
            error_rates.append((running_errors / running_sifted) * 100.0)

    if len(sifted_steps) > 0:
        line_color = RED_COLOR if result.eve_enabled else GREEN_COLOR
        ax.plot(sifted_steps, error_rates, color=line_color, linewidth=2.5, label="Cumulative QBER (%)")
        
        theo_val = 25.0 if result.eve_enabled else 0.0
        ax.axhline(theo_val, color=CYAN_ACCENT, linestyle="--", linewidth=1.8, label=f"Theoretical ({theo_val:.1f}%)")

    ax.set_xlabel("Sifted Bit Index", color=TEXT_COLOR, fontsize=10)
    ax.set_ylabel("Observed Error Rate (%)", color=TEXT_COLOR, fontsize=10)
    mode_label = "With Eve (Intercept-Resend)" if result.eve_enabled else "Without Eve (Direct Channel)"
    ax.set_title(f"Cumulative Error Rate Trajectory — {mode_label}", color=TEXT_COLOR, fontsize=13, fontweight="bold")
    ax.set_ylim(-1, 50 if result.eve_enabled else 10)
    ax.legend(facecolor=PANEL_BG, edgecolor="#334155", labelcolor=TEXT_COLOR, fontsize=9)

    plt.tight_layout()
    return fig


def plot_basis_matching_pie(result: ProtocolResult) -> plt.Figure:
    """
    Generates a breakdown of matching vs discarded bases.
    """
    fig, ax = plt.subplots(figsize=(5, 4), facecolor=NAVY_BG)
    ax.set_facecolor(NAVY_BG)

    matched = result.sifted_bits_count
    discarded = result.discarded_bits_count

    sizes = [matched, discarded]
    labels = [f"Retained ({matched})", f"Discarded ({discarded})"]
    colors = [CYAN_ACCENT, "#475569"]
    explode = (0.05, 0)

    wedges, texts, autotexts = ax.pie(
        sizes, explode=explode, labels=labels, colors=colors,
        autopct="%1.1f%%", startangle=140,
        textprops=dict(color=TEXT_COLOR, fontsize=10),
        wedgeprops=dict(edgecolor="#0b1120", linewidth=2)
    )

    for autotext in autotexts:
        autotext.set_color("#0b1120")
        autotext.set_fontweight("bold")

    ax.set_title("Basis Sifting Efficiency (~50% Ideal)", color=TEXT_COLOR, fontsize=12, fontweight="bold")
    plt.tight_layout()
    return fig


def plot_repeated_trials(trials_data: Dict[str, Any]) -> plt.Figure:
    """
    Visualizes distribution across repeated Monte Carlo trials (Enhancement 2).
    """
    fig, ax = plt.subplots(figsize=(8, 4), facecolor=NAVY_BG)
    setup_dark_style(ax)

    trial_nums = [t["Trial"] for t in trials_data["trial_results"]]
    qbers = [t["QBER (%)"] for t in trials_data["trial_results"]]
    mean_val = trials_data["mean_qber"]
    theo_val = trials_data["theoretical_qber"]

    color = RED_COLOR if trials_data["eve_present"] else GREEN_COLOR

    ax.scatter(trial_nums, qbers, color=color, s=70, edgecolor=CYAN_ACCENT, linewidth=1.5, zorder=3, label="Trial Outcome")
    ax.plot(trial_nums, qbers, color=color, alpha=0.4, linestyle=":", zorder=2)
    
    # Mean line
    ax.axhline(mean_val, color=CYAN_ACCENT, linewidth=2, linestyle="-", label=f"Empirical Mean ({mean_val:.2f}%)")
    # Theoretical line
    ax.axhline(theo_val, color=VIOLET_ACCENT, linewidth=2, linestyle="--", label=f"Theoretical ({theo_val:.2f}%)")

    ax.set_xlabel("Trial Number", color=TEXT_COLOR, fontsize=10)
    ax.set_ylabel("Measured QBER (%)", color=TEXT_COLOR, fontsize=10)
    mode = "With Eve" if trials_data["eve_present"] else "Without Eve"
    ax.set_title(f"Monte Carlo Variance Across {trials_data['n_trials']} Trials — {mode}", color=TEXT_COLOR, fontsize=13, fontweight="bold")
    ax.legend(facecolor=PANEL_BG, edgecolor="#334155", labelcolor=TEXT_COLOR, fontsize=9)
    ax.set_ylim(-1, max(40.0, max(qbers + [30.0]) + 5))

    plt.tight_layout()
    return fig
