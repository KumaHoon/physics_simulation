"""
Layer 3 — Application Layer (Strawberry Fields)

Implements the Quantum Optical Bus model that generates Wigner functions
for time-bin encoded squeezed states.
"""

from typing import List, Tuple

import numpy as np

# Compat patches must be applied before importing Strawberry Fields.
import quantum_optical_bus.compat  # noqa: F401

import strawberryfields as sf
from strawberryfields.ops import Sgate, Rgate

from .interface import calculate_squeezing


class QuantumBusModel:
    """
    Quantum optical bus simulation engine.

    Runs Strawberry Fields Gaussian simulations for *num_bins*
    independent time-bins, each with its own pump power and phase.
    """

    def __init__(self, num_bins: int = 4) -> None:
        self.num_bins = num_bins

    def run_simulation(
        self,
        powers: List[float],
        phases: List[float],
        grid_limit: float = 4.0,
        grid_points: int = 100,
    ) -> Tuple[list, np.ndarray]:
        """
        Simulate all time-bins and compute Wigner functions.

        Parameters
        ----------
        powers : list[float]
            Pump power per bin (mW).
        phases : list[float]
            Phase shift per bin (rad).
        grid_limit : float
            Half-width of the Wigner-function grid.
        grid_points : int
            Number of grid points along each axis.

        Returns
        -------
        wigner_data : list[tuple(np.ndarray, float, float)]
            (W, r, θ) for each bin.
        xvec : np.ndarray
            Coordinate vector for the Wigner grid.
        """
        xvec = np.linspace(-grid_limit, grid_limit, grid_points)
        wigner_data = []

        for i in range(self.num_bins):
            r_param = calculate_squeezing(powers[i])
            theta_param = phases[i]

            prog = sf.Program(1)
            eng = sf.Engine("gaussian")

            with prog.context as q:
                if r_param > 0:
                    Sgate(r_param) | q[0]
                if theta_param != 0:
                    Rgate(theta_param) | q[0]

            result = eng.run(prog)
            W = result.state.wigner(0, xvec, xvec)
            wigner_data.append((W, r_param, theta_param))

        return wigner_data, xvec
