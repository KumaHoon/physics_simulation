"""
Generate a professional calibration demo GIF for grad school portfolio.

Two-phase animation:
  Phase 1 — Power ramp (0 → 200 mW): vacuum circle flattens into squeezed ellipse
  Phase 2 — Loss ramp  (0 → 2 dB):   squeezed ellipse becomes round/fuzzy (decoherence)

Output: assets/calibration_demo.gif

Usage:
    python scripts/generate_calibration_demo.py
"""

import sys
import pathlib

_SRC = pathlib.Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import quantum_optical_bus.compat  # noqa: F401

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import matplotlib.patches as mpatches

import strawberryfields as sf
from strawberryfields.ops import Sgate, LossChannel

# ── Output ────────────────────────────────────────────────────────
ASSETS = pathlib.Path(__file__).resolve().parents[1] / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)
OUT_PATH = ASSETS / "calibration_demo.gif"

# ── Physics constants ─────────────────────────────────────────────
ETA = 0.05          # coupling: r = eta * sqrt(P)
GRID_LIM = 5.0
GRID_PTS = 100
xvec = np.linspace(-GRID_LIM, GRID_LIM, GRID_PTS)

# ── Animation timeline ────────────────────────────────────────────
N_PHASE1 = 40       # frames: power 0 → 200 mW
N_PHASE2 = 30       # frames: loss  0 → 2 dB
N_TOTAL = N_PHASE1 + N_PHASE2

powers = np.concatenate([
    np.linspace(0, 200, N_PHASE1),
    np.full(N_PHASE2, 200.0),
])
losses_db = np.concatenate([
    np.zeros(N_PHASE1),
    np.linspace(0, 2.0, N_PHASE2),
])

# ── Pre-compute all Wigner functions ─────────────────────────────
print(f"Pre-computing {N_TOTAL} Wigner frames ...")
cache = []
for i in range(N_TOTAL):
    P = powers[i]
    L_db = losses_db[i]

    r = ETA * np.sqrt(P)
    sq_db = -10 * np.log10(np.exp(-2 * r)) if r > 0 else 0.0
    transmittance = 10 ** (-L_db / 10.0) if L_db > 0 else 1.0

    prog = sf.Program(1)
    with prog.context as q:
        if r > 0:
            Sgate(r) | q[0]
        if transmittance < 1.0:
            LossChannel(transmittance) | q[0]

    result = sf.Engine("gaussian").run(prog)
    W = result.state.wigner(0, xvec, xvec)
    cov = result.state.cov()
    var_x = cov[0, 0] / 2.0
    var_p = cov[1, 1] / 2.0

    cache.append({
        "W": W, "r": r, "sq_db": sq_db,
        "P": P, "L_db": L_db,
        "transmittance": transmittance,
        "var_x": var_x, "var_p": var_p,
    })
print("Done.")

# ── Dark theme ────────────────────────────────────────────────────
BG      = "#0e1117"
PANEL   = "#161b22"
ACCENT  = "#58a6ff"
RED     = "#ff6b6b"
GREEN   = "#3fb950"
ORANGE  = "#f0883e"
GRAY    = "#8b949e"
WHITE   = "#e6edf3"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": PANEL,
    "axes.edgecolor": GRAY,
    "axes.labelcolor": WHITE,
    "text.color": WHITE,
    "xtick.color": GRAY,
    "ytick.color": GRAY,
    "font.family": "monospace",
    "font.size": 11,
})

# ── Figure layout ─────────────────────────────────────────────────
fig = plt.figure(figsize=(14, 6))

# Left panel: dashboard metrics
ax_dash = fig.add_axes([0.04, 0.08, 0.38, 0.82])
ax_dash.set_xlim(0, 10)
ax_dash.set_ylim(0, 10)
ax_dash.axis("off")

# Right panel: Wigner function
ax_wig = fig.add_axes([0.50, 0.08, 0.46, 0.82])

# Title
fig.text(0.50, 0.96,
         "TDM Optical Bus  \u2014  Squeezed Light Calibration",
         ha="center", fontsize=16, fontweight="bold", color=WHITE)


def draw_bar(ax, x, y, w, h, frac, color, label_left, label_right):
    """Draw a horizontal progress bar."""
    ax.add_patch(mpatches.FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.08",
        facecolor="#21262d", edgecolor=GRAY, linewidth=0.8))
    ax.add_patch(mpatches.FancyBboxPatch(
        (x, y), w * frac, h, boxstyle="round,pad=0.08",
        facecolor=color, edgecolor="none", alpha=0.85))
    ax.text(x - 0.15, y + h / 2, label_left,
            ha="right", va="center", fontsize=10, color=GRAY)
    ax.text(x + w + 0.15, y + h / 2, label_right,
            ha="left", va="center", fontsize=10, color=WHITE, fontweight="bold")


def update(frame):
    d = cache[frame]
    phase = "Phase 1: Power Sweep" if frame < N_PHASE1 else "Phase 2: Loss Channel"
    phase_color = ACCENT if frame < N_PHASE1 else ORANGE

    # ── Left panel ──
    ax_dash.cla()
    ax_dash.set_xlim(0, 10)
    ax_dash.set_ylim(0, 10)
    ax_dash.axis("off")

    # Phase indicator
    ax_dash.add_patch(mpatches.FancyBboxPatch(
        (0.3, 8.8), 9.2, 0.9, boxstyle="round,pad=0.15",
        facecolor=phase_color, edgecolor="none", alpha=0.2))
    ax_dash.text(4.9, 9.25, phase, ha="center", va="center",
                 fontsize=13, fontweight="bold", color=phase_color)

    # Pump Power bar
    draw_bar(ax_dash, 3.0, 7.6, 5.5, 0.55,
             d["P"] / 200.0, ACCENT,
             "Pump Power", f'{d["P"]:.0f} mW')

    # Loss bar
    draw_bar(ax_dash, 3.0, 6.6, 5.5, 0.55,
             d["L_db"] / 2.0, ORANGE,
             "Loss", f'{d["L_db"]:.2f} dB')

    # Divider
    ax_dash.plot([0.5, 9.5], [6.15, 6.15], color=GRAY, lw=0.5, alpha=0.4)

    # Metrics
    ax_dash.text(4.9, 5.5, "Calibration Metrics",
                 ha="center", fontsize=12, fontweight="bold", color=WHITE)

    # r parameter
    ax_dash.text(1.0, 4.6, "Squeezing Param (r):", fontsize=11, color=GRAY)
    ax_dash.text(8.5, 4.6, f"{d['r']:.4f}", fontsize=13,
                 fontweight="bold", color=GREEN, ha="right")

    # Squeezing dB — large and red
    ax_dash.add_patch(mpatches.FancyBboxPatch(
        (0.5, 2.9), 9.0, 1.3, boxstyle="round,pad=0.15",
        facecolor="#2d1015", edgecolor=RED, linewidth=1.5, alpha=0.7))
    ax_dash.text(4.9, 3.85, "SQUEEZING LEVEL",
                 ha="center", fontsize=10, color=GRAY, fontweight="bold")
    ax_dash.text(4.9, 3.25, f"-{d['sq_db']:.2f} dB",
                 ha="center", fontsize=22, fontweight="bold", color=RED)

    # Quadrature variances
    ax_dash.text(1.0, 2.2, "Var(x):", fontsize=10, color=GRAY)
    ax_dash.text(3.5, 2.2, f"{d['var_x']:.4f}", fontsize=11,
                 fontweight="bold", color=GREEN)
    ax_dash.text(5.5, 2.2, "Var(p):", fontsize=10, color=GRAY)
    ax_dash.text(8.0, 2.2, f"{d['var_p']:.4f}", fontsize=11,
                 fontweight="bold", color=RED)

    # Transmissivity
    ax_dash.text(1.0, 1.4, "Transmissivity:", fontsize=10, color=GRAY)
    eta_str = f"{d['transmittance']:.4f}"
    eta_color = GREEN if d["transmittance"] > 0.9 else (ORANGE if d["transmittance"] > 0.5 else RED)
    ax_dash.text(5.5, 1.4, eta_str, fontsize=11, fontweight="bold", color=eta_color)

    # Frame counter
    ax_dash.text(4.9, 0.3, f"Frame {frame + 1}/{N_TOTAL}",
                 ha="center", fontsize=9, color=GRAY, alpha=0.6)

    # ── Right panel: Wigner ──
    ax_wig.cla()
    ax_wig.contourf(xvec, xvec, d["W"], levels=80, cmap="RdBu_r")
    ax_wig.set_xlim(-GRID_LIM, GRID_LIM)
    ax_wig.set_ylim(-GRID_LIM, GRID_LIM)
    ax_wig.set_xlabel("x  (position quadrature)", fontsize=11)
    ax_wig.set_ylabel("p  (momentum quadrature)", fontsize=11)
    ax_wig.set_title(
        f"Wigner Function    r = {d['r']:.3f}",
        fontsize=13, fontweight="bold", color=WHITE, pad=10)
    ax_wig.set_aspect("equal")
    ax_wig.grid(True, alpha=0.08, color=GRAY)


print(f"Rendering {N_TOTAL} frames ...")
anim = FuncAnimation(fig, update, frames=N_TOTAL, blit=False)
anim.save(str(OUT_PATH), writer=PillowWriter(fps=8), dpi=110)
plt.close(fig)
print(f"[OK] Saved to {OUT_PATH}")
