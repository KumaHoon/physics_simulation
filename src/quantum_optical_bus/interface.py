"""
Layer 2 — Interface Layer

Maps physical pump power (mW) to the quantum squeezing parameter *r*
using a phenomenological model for Lithium Niobate waveguides.
"""

import numpy as np

# Phenomenological coupling efficiency.
# Tuned so that 100 mW → r ≈ 1.0.
_COUPLING_EFFICIENCY = 0.1


def calculate_squeezing(pump_power_mw: float) -> float:
    """
    Convert pump power to squeezing parameter.

    Parameters
    ----------
    pump_power_mw : float
        Pump power in milliwatts (≥ 0).

    Returns
    -------
    r : float
        Squeezing parameter for a Strawberry Fields ``Sgate``.
    """
    return _COUPLING_EFFICIENCY * np.sqrt(pump_power_mw)
