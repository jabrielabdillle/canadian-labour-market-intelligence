"""Chart Alberta and Canada's monthly unemployment rates."""
from datetime import date
from pathlib import Path
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTPUT = Path(__file__).resolve().parent / "outputs"


def main():
    if not (OUTPUT / "labour.sqlite").exists():
        raise SystemExit("Run python3 pipeline.py first.")
    fig, ax = plt.subplots(figsize=(10, 4.8), layout="constrained")
    with sqlite3.connect(OUTPUT / "labour.sqlite") as db:
        for geography, color in [("Alberta", "#087F8C"), ("Canada", "#273B64")]:
            rows = db.execute("""
                SELECT month, rate FROM rates
                WHERE metric = 'Unemployment rate' AND geography = ?
                ORDER BY month
            """, (geography,)).fetchall()
            ax.plot([date.fromisoformat(month) for month, _ in rows],
                    [rate for _, rate in rows], color=color, label=geography)
    ax.set(title="Monthly unemployment in Alberta and Canada",
           ylabel="Unemployment rate (%)")
    ax.text(0, -0.18, "Source: Statistics Canada, Labour Force Survey, table 14-10-0287-01\n"
            "Seasonally adjusted estimates, ages 15 and over",
            transform=ax.transAxes, fontsize=9, color="#42526B", va="top")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(OUTPUT / "unemployment_trends.png", dpi=150)


if __name__ == "__main__":
    main()
