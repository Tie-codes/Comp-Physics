"""Plot voltage vs current (with error bars) for each plasma power dataset.

Data format (per file, per voltage block):
    <setpoint>V
    Time - Plot 0  Amplitude - Plot 0
    <idx>\tVc
    <idx>\tVc_err
    <idx>\tIc
    <idx>\tIc_err
"""

import re
from pathlib import Path

import matplotlib.pyplot as plt

DATA_DIR = Path(__file__).parent / "data"
OUT_DIR = Path(__file__).parent / "plots"
OUT_DIR.mkdir(exist_ok=True)

POWERS = ["20W", "40W", "60W", "80W"]

SETPOINT_RE = re.compile(r"^\s*(\d+)\s*[Vv]\s*$")


def parse_file(path: Path):
    """Return list of (setpoint_V, Vc, Vc_err, Ic, Ic_err) tuples."""
    lines = path.read_text().splitlines()
    points = []
    i = 0
    while i < len(lines):
        m = SETPOINT_RE.match(lines[i])
        if not m:
            i += 1
            continue
        setpoint = int(m.group(1))
        # Expect a header line next, then four data lines.
        if i + 1 >= len(lines) or "Amplitude" not in lines[i + 1]:
            i += 1
            continue
        try:
            vals = []
            for k in range(4):
                parts = lines[i + 2 + k].split("\t")
                vals.append(float(parts[1]))
            Vc, Vc_err, Ic, Ic_err = vals
            points.append((setpoint, Vc, Vc_err, Ic, Ic_err))
            i += 6
        except (IndexError, ValueError):
            i += 1
    return points


def plot_power(power: str):
    path = DATA_DIR / f"{power}.txt"
    points = parse_file(path)
    points.sort(key=lambda p: p[1])  # sort by measured voltage

    Vc = [p[1] for p in points]
    Vc_err = [p[2] for p in points]
    Ic = [p[3] for p in points]
    Ic_err = [p[4] for p in points]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.errorbar(
        Vc, Ic,
        xerr=Vc_err, yerr=Ic_err,
        fmt="o", markersize=5,
        color="C0", ecolor="gray",
        elinewidth=1, capsize=3,
        label=f"{power} measurements",
    )
    ax.set_xlabel("Voltage $V_c$ (V)")
    ax.set_ylabel("Current $I_c$ (A)")
    ax.set_title(f"I–V Characteristic at {power}")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()

    out = OUT_DIR / f"IV_{power}.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"{power}: {len(points)} points -> {out}")


if __name__ == "__main__":
    for p in POWERS:
        plot_power(p)
