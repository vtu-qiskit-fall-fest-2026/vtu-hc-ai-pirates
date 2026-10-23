"""
QuantumShield - Architecture Diagram Generator
Generates a publication-grade, high-DPI architecture diagram (assets/architecture.png).
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Dark theme palette
BG_COLOR = "#0b1120"
CARD_COLOR = "#111c38"
CYAN = "#06b6d4"
VIOLET = "#a855f7"
RED = "#ef4444"
GREEN = "#10b981"
TEXT = "#f8fafc"
MUTED = "#94a3b8"
LINE_COLOR = "#38bdf8"


def draw_box(ax, x, y, w, h, title, subtitle, border_color=CYAN, fill_color=CARD_COLOR):
    """Draws a themed rounded box with title and subtitle."""
    box = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.03,rounding_size=0.04",
        facecolor=fill_color,
        edgecolor=border_color,
        linewidth=2,
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h * 0.65, title, ha="center", va="center", color=TEXT, fontsize=11, fontweight="bold")
    ax.text(x + w / 2, y + h * 0.32, subtitle, ha="center", va="center", color=MUTED, fontsize=8.5)


def draw_arrow(ax, x1, y1, x2, y2, color=CYAN, style="->", text=None):
    """Draws a labeled connection arrow."""
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(arrowstyle=style, color=color, lw=2.2, shrinkA=4, shrinkB=4),
    )
    if text:
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2 + 0.03
        ax.text(mid_x, mid_y, text, ha="center", va="bottom", color=color, fontsize=8.5, fontweight="bold")


def generate_diagram(output_path="assets/architecture.png"):
    fig, ax = plt.subplots(figsize=(13, 7.5), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Header
    ax.text(0.5, 0.95, "QuantumShield: BB84 Architecture & Eavesdropping Detection", ha="center", va="center", color=TEXT, fontsize=17, fontweight="bold")
    ax.text(0.5, 0.90, "Qiskit Fall Fest 2026 | Team AI Pirates (VTU-QFF-HC-0142)", ha="center", va="center", color=CYAN, fontsize=11)

    # Alice Box
    draw_box(ax, 0.04, 0.62, 0.22, 0.20, "1. Alice (Transmitter)", "Random Bits (0/1)\nRandom Bases (Z/X)", CYAN)

    # Qiskit Preparation
    draw_box(ax, 0.32, 0.62, 0.22, 0.20, "2. Qiskit State Prep", "X Gate & H Gate\n|0⟩, |1⟩, |+⟩, |-⟩", VIOLET)

    # Quantum Channel (Center)
    draw_box(ax, 0.60, 0.62, 0.16, 0.20, "Quantum Channel", "Single-photon stream\nCoherent or tapped", LINE_COLOR)

    # Bob Box
    draw_box(ax, 0.82, 0.62, 0.15, 0.20, "3. Bob (Receiver)", "Random Bases (Z/X)\nProjective Measurement", GREEN)

    # Arrows main flow
    draw_arrow(ax, 0.26, 0.72, 0.32, 0.72, CYAN, "->", "Bit & Basis")
    draw_arrow(ax, 0.54, 0.72, 0.60, 0.72, VIOLET, "->", "|ψ⟩ state")
    draw_arrow(ax, 0.76, 0.72, 0.82, 0.72, LINE_COLOR, "->", "|ψ'⟩ received")

    # Eve Intercept Branch (Top middle)
    draw_box(ax, 0.58, 0.28, 0.20, 0.18, "Eve (Attacker)", "Intercept-Resend Attack\nRandom basis measurement\nState collapse (25% QBER)", RED)
    
    # Arrows to and from Eve
    ax.annotate(
        "", xy=(0.68, 0.46), xytext=(0.68, 0.62),
        arrowprops=dict(arrowstyle="->", color=RED, lw=2, linestyle="dashed"),
    )
    ax.text(0.70, 0.54, "Tap / Intercept", color=RED, fontsize=8.5, fontweight="bold")

    ax.annotate(
        "", xy=(0.82, 0.65), xytext=(0.78, 0.40),
        arrowprops=dict(arrowstyle="->", color=RED, lw=2, linestyle="dashed"),
    )
    ax.text(0.81, 0.49, "Resend Collapsed", color=RED, fontsize=8, fontweight="bold")

    # Bottom Reconciliation Layer
    # Public Classical Channel
    draw_box(ax, 0.08, 0.04, 0.25, 0.16, "4. Basis Sifting", "Public Classical Channel\nAlice & Bob announce bases\nKeep matches (~50%)", CYAN)

    # QBER Analysis & Security Verdict
    draw_box(ax, 0.40, 0.04, 0.28, 0.16, "5. QBER Calculation", "QBER = Mismatches / Sifted\nNo Eve: 0.0% (Secure)\nWith Eve: ~25.0% (Attack)", GREEN)

    # Final Key & OTP Demo
    draw_box(ax, 0.74, 0.04, 0.22, 0.16, "6. Key Use / OTP Demo", "Verified Sifted Key\nOne-Time Pad Encryption\nAbort if QBER > 11%", VIOLET)

    # Inter-layer arrows
    draw_arrow(ax, 0.15, 0.62, 0.15, 0.20, CYAN, "->", "Alice Bases")
    draw_arrow(ax, 0.88, 0.62, 0.88, 0.20, GREEN, "->", "Bob Bases")
    draw_arrow(ax, 0.33, 0.12, 0.40, 0.12, CYAN, "->", "Sifted Bits")
    draw_arrow(ax, 0.68, 0.12, 0.74, 0.12, GREEN, "->", "Clean Key")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close()
    print(f"Architecture diagram saved to {output_path}")


if __name__ == "__main__":
    generate_diagram()
