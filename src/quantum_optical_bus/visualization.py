"""
Visualization module — BusVisualizer

Handles all Matplotlib plotting for the Quantum Optical Bus dashboard.
Separated from the simulation logic (Single Responsibility Principle).
"""

from typing import List

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec


class BusVisualizer:
    """
    Renders hardware mode profiles and software Wigner functions.

    Parameters
    ----------
    bin_labels : list[str]
        Display labels for each time-bin (e.g. ["Bin 0", …, "Bin 3"]).
    """

    def __init__(self, bin_labels: List[str]) -> None:
        self.bin_labels = bin_labels

    # ------------------------------------------------------------------
    # Hardware panel (left side)
    # ------------------------------------------------------------------

    def plot_hardware(
        self,
        ax: plt.Axes,
        ez_data: np.ndarray,
        extent: list,
        n_eff: float,
        mode_area: float,
    ) -> None:
        """Plot the waveguide mode profile on *ax*."""
        ax.set_title(
            "Hardware Layer (Fixed)\nLN Ridge Waveguide Simulation (Meep)",
            fontsize=12,
            fontweight="bold",
        )
        ax.imshow(ez_data, extent=extent, cmap="RdBu", origin="lower")
        ax.set_xlabel("x (μm)")
        ax.set_ylabel("y (μm)")
        ax.text(
            0.05,
            0.95,
            f"n_eff: {n_eff:.2f}\nMode Area: {mode_area:.2f} μm²",
            transform=ax.transAxes,
            color="white",
            ha="left",
            va="top",
            fontsize=10,
            bbox=dict(facecolor="black", alpha=0.6, edgecolor="none"),
        )

    # ------------------------------------------------------------------
    # Software panel (right side — Wigner functions)
    # ------------------------------------------------------------------

    def plot_software(
        self,
        fig: Figure,
        gs: GridSpec,
        wigner_data: list,
        xvec: np.ndarray,
        powers: List[float],
        phases: List[float],
    ) -> None:
        """Plot Wigner contour plots for each time-bin."""
        for i, (W, _r, _theta) in enumerate(wigner_data):
            row, col = divmod(i, 2)
            ax = fig.add_subplot(gs[row, 2 + col])

            ax.contourf(xvec, xvec, W, levels=20, cmap="viridis")
            ax.set_title(
                f"{self.bin_labels[i]}\nP={powers[i]}mW, Phase={phases[i]:.2f}",
                fontsize=10,
            )

            if row == 1:
                ax.set_xlabel("x")
            else:
                ax.set_xticks([])

            if col == 0:
                ax.set_ylabel("p")
            else:
                ax.set_yticks([])

            ax.set_aspect("equal")
