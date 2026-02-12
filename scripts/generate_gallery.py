"""
Gallery generator — produces result images for the README.

Usage:
    python scripts/generate_gallery.py
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from quantum_optical_bus.hardware import run_hardware_simulation
from quantum_optical_bus.application import QuantumBusModel
from quantum_optical_bus.visualization import BusVisualizer

# Output directory
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

BIN_LABELS = ["Bin 0", "Bin 1", "Bin 2", "Bin 3"]


def generate_result(filename, title, scenario_powers, scenario_phases, description):
    """Generate a single scenario image."""
    filepath = ASSETS_DIR / filename
    print(f"Generating {filepath} ...")

    # Layer 1 — Hardware
    n_eff, mode_area, ez_data, extent = run_hardware_simulation()

    # Layer 3 — Application
    model = QuantumBusModel(num_bins=4)
    wigner_data, xvec = model.run_simulation(scenario_powers, scenario_phases)

    # Visualization
    view = BusVisualizer(BIN_LABELS)
    fig = plt.figure(figsize=(16, 7))
    gs = fig.add_gridspec(2, 4, width_ratios=[1, 1, 1, 1])

    # Hardware panel (left)
    ax_hw = fig.add_subplot(gs[:, 0:2])
    ax_hw.set_title(
        "Fixed Hardware Layer (Meep)\nLN Ridge Waveguide",
        fontsize=14, fontweight="bold", color="navy",
    )
    ax_hw.imshow(ez_data, extent=extent, cmap="RdBu", origin="lower")
    ax_hw.set_xlabel("x (μm)")
    ax_hw.set_ylabel("y (μm)")
    ax_hw.text(
        0.05, 0.95,
        f"n_eff: {n_eff:.2f}\nMode Area: {mode_area:.2f} μm²",
        transform=ax_hw.transAxes, color="white", ha="left", va="top",
        fontsize=11, bbox=dict(facecolor="black", alpha=0.6, edgecolor="none"),
    )

    # Software panel (right) — with extra annotations
    for i, (W, r_param, theta_param) in enumerate(wigner_data):
        row, col = divmod(i, 2)
        ax = fig.add_subplot(gs[row, 2 + col])
        ax.contourf(xvec, xvec, W, levels=20, cmap="viridis")

        state_str = "Squeezed" if scenario_powers[i] > 0 else "Vacuum"
        ax.set_title(
            f"{BIN_LABELS[i]}\nP={scenario_powers[i]}mW, Ph={scenario_phases[i]:.2f}\n({state_str})",
            fontsize=11,
        )
        if row == 0:
            ax.set_xticks([])
        else:
            ax.set_xlabel("x")
        if col == 1:
            ax.set_yticks([])
        else:
            ax.set_ylabel("p")
        ax.set_aspect("equal")

    plt.suptitle(f"Scenario: {title}\n{description}", fontsize=16, y=0.99)
    plt.tight_layout()
    plt.savefig(filepath, dpi=100)
    plt.close()


# ------------------------------------------------------------------
# Scenarios
# ------------------------------------------------------------------

if __name__ == "__main__":
    # 1. Vacuum / Baseline
    generate_result(
        "result_vacuum.png",
        "Baseline System Check",
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        "Insight: With 0mW Pump Power, the 'Bus' transmits pure Vacuum States (Shot Noise Unit).",
    )

    # 2. Amplitude vs Phase Encoding
    generate_result(
        "result_encoding.png",
        "Orthogonal Information Encoding",
        [50, 50, 0, 0],
        [0, 1.57, 0, 0],
        "Insight: Bin 0 is Amplitude Squeezed (Horizontal), Bin 1 is Phase Squeezed (Vertical).\n"
        "Demonstrates independent control on the same waveguide.",
    )

    # 3. Analog Gradient
    generate_result(
        "result_gradient.png",
        "Analog Quantum Control",
        [0, 10, 40, 90],
        [0, 0, 0, 0],
        "Insight: Increasing Pump Power (0→90mW) progressively augments the Squeezing strength.\n"
        "Demonstrates the Continuous Variable (CV) nature of the system.",
    )
