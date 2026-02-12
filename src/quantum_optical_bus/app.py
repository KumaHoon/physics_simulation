import marimo

__generated_with = "0.19.9"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt

    # Import from the layered package
    from quantum_optical_bus.hardware import run_hardware_simulation
    from quantum_optical_bus.application import QuantumBusModel
    from quantum_optical_bus.visualization import BusVisualizer

    return BusVisualizer, QuantumBusModel, mo, np, plt, run_hardware_simulation


@app.cell
def _(mo):
    mo.md(r"""
    # "Fixed Hardware, Dynamic Control" Simulation

    This simulator demonstrates the concept of using a **fixed hardware resource** (a Lithium Niobate waveguide) to generate **dynamically controllable quantum states** (Time-bin encoded squeezed light).

    - **Left Panel**: The physical **Hardware Layer** (Meep Simulation). Fixed geometry.
    - **Right Panel**: The **Software/Control Layer** (Strawberry Fields). Dynamic control of pump power and phase for multiple time-bins.
    """)
    return


@app.cell
def _(run_hardware_simulation):
    # Layer 1: Hardware — run once, fixed geometry
    n_eff, mode_area, ez_data, extent = run_hardware_simulation()
    return extent, ez_data, mode_area, n_eff


@app.cell
def _(mo):
    # Layer 3: Application — UI Controls

    mo.md("### Control Layer (CS Architecture)")

    bins = ["Bin 0", "Bin 1", "Bin 2", "Bin 3"]

    power_sliders = [mo.ui.slider(0, 100, step=1, label=f"{b} Power (mW)") for b in bins]
    phase_sliders = [mo.ui.slider(0, 2*3.14, step=0.1, label=f"{b} Phase (rad)") for b in bins]

    ui_controls = mo.vstack([
        mo.md("**Pump Power Controls**"),
        mo.hstack(power_sliders),
        mo.md("**Phase Shift Controls**"),
        mo.hstack(phase_sliders)
    ])

    ui_controls
    return bins, phase_sliders, power_sliders


@app.cell
def _(
    BusVisualizer,
    QuantumBusModel,
    bins,
    extent,
    ez_data,
    mo,
    mode_area,
    n_eff,
    phase_sliders,
    plt,
    power_sliders,
):
    # Controller: wires Model ↔ View

    # 1. Retrieve control values
    powers = [s.value for s in power_sliders]
    phases = [s.value for s in phase_sliders]

    # 2. Run simulation (Layer 3)
    model = QuantumBusModel(num_bins=4)
    wigner_data, xvec = model.run_simulation(powers, phases)

    # 3. Visualize
    view = BusVisualizer(bins)
    fig = plt.figure(figsize=(14, 6))
    gs = fig.add_gridspec(2, 4, width_ratios=[1, 1, 1, 1])

    ax_hw = fig.add_subplot(gs[:, 0:2])
    view.plot_hardware(ax_hw, ez_data, extent, n_eff, mode_area)
    view.plot_software(fig, gs, wigner_data, xvec, powers, phases)

    plt.suptitle("Fixed Hardware (Meep) vs Dynamic Control (Strawberry Fields)", fontsize=16, y=0.98)
    plt.tight_layout()
    mo.mpl.interactive(fig)
    return fig, gs, model, phases, powers, view, wigner_data, xvec


if __name__ == "__main__":
    app.run()
