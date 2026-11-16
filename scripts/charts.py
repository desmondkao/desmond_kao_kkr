"""Regenerate every chart in docs/charts/: python scripts/charts.py

algorithms and fairness read results/*.csv (python -m elevator_sim.benchmark);
overload and load_sweep run the simulator directly with fixed seeds.
"""

from __future__ import annotations

import csv
import sys
from dataclasses import replace
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))  # so it runs from a checkout without installing

from elevator_sim.benchmark import EXPRESS, STANDARD
from elevator_sim.dispatch import make_dispatcher
from elevator_sim.engine import Simulation
from elevator_sim.scenarios import SCENARIOS, generate

OUT = ROOT / "docs" / "charts"
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
# One fixed color per dispatcher across every chart.
COLOR = {"etd": "#2a78d6", "zone": "#eb6834", "etd + express": "#1baf7a",
         "round-robin": "#eda100", "nearest": "#e87ba4",
         "etd-p1": "#9cc2f0", "etd-p2": "#2a78d6", "etd-p4": "#0d3f7f"}
BASELINES = ("round-robin", "nearest", "zone", "etd")
LABEL = {"etd": "ETD", "zone": "Zone", "etd + express": "ETD + express", "round-robin": "Round robin",
         "nearest": "Nearest car", "etd-p1": "ETD, p = 1", "etd-p2": "ETD, p = 2", "etd-p4": "ETD, p = 4"}
ETD_NOTE = "ETD = estimated time to destination. "

plt.rcParams.update({
    "figure.figsize": (16, 9), "figure.dpi": 100, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "font.size": 16, "axes.titlesize": 18, "axes.labelsize": 16, "figure.titlesize": 24,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 1, "axes.axisbelow": True, "lines.linewidth": 2.5, "legend.frameon": False,
})


def run(config, requests, dispatcher):
    return Simulation(config, requests, make_dispatcher(dispatcher, config.floors)).run()


def building(name, dwell):
    """'etd + express' means ETD on the express building; anything else runs on the standard one."""
    return replace(EXPRESS if name == "etd + express" else STANDARD, dwell=dwell)


def read_rows(name):
    with open(ROOT / "results" / f"{name}.csv") as f:
        return [{k: (float(v) if k not in ("building", "scenario", "dispatcher") else v) for k, v in r.items()}
                for r in csv.DictReader(f)]


def save(fig, name, title, subtitle):
    fig.suptitle(title, x=0.06, ha="left", y=0.97, color=INK, fontweight="bold")
    fig.text(0.06, 0.905, subtitle, color=MUTED, fontsize=16)
    fig.savefig(OUT / name, facecolor=SURFACE)
    plt.close(fig)
    print("wrote", OUT / name)


def algorithms():
    fig, axes = plt.subplots(1, 2, sharey=True)
    fig.subplots_adjust(top=0.80, bottom=0.17, wspace=0.08)
    offsets = np.linspace(-0.27, 0.27, len(BASELINES))
    for ax, dwell in zip(axes, (0, 1)):
        rows = [r for r in read_rows(f"algorithms_dwell{dwell}") if r["rate"] == 0.8]
        for d, dx in zip(BASELINES, offsets):
            pts = [next(r for r in rows if r["scenario"] == s and r["dispatcher"] == d) for s in SCENARIOS]
            ax.errorbar(np.arange(len(SCENARIOS)) + dx, [r["total_mean"] for r in pts],
                        yerr=[r["total_ci95"] for r in pts], fmt="o", ms=13, color=COLOR[d], capsize=4,
                        label=LABEL[d], elinewidth=2, markeredgecolor=SURFACE, markeredgewidth=1.5)
        ax.set_yscale("log")
        ax.set_ylim(15, 230)
        ax.set_xticks(range(len(SCENARIOS)), SCENARIOS)
        ax.set_title(f"dwell = {dwell} " + ("(stopping is free)" if dwell == 0 else "(each stop costs 1 tick)"),
                     loc="left", color=INK)
        ax.grid(axis="x", visible=False)
    ticks = [20, 30, 50, 100, 200]
    axes[0].set_yticks(ticks, [str(t) for t in ticks])
    axes[0].yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    axes[0].set_ylabel("mean total time, ticks (log scale)")
    axes[0].legend(loc="upper center", bbox_to_anchor=(1.04, -0.09), ncol=4)
    save(fig, "algorithms.png", "ETD wins every pattern when stops are free; with 1-tick stops it loses up-peak",
         ETD_NOTE + "Mean total time ± 95% CI over 10 seeds at 0.8 passengers/tick, 30 floors, 4 cars")


def binned_total(name, rate, dwell, seeds=3, duration=1200, width=60):
    """Mean total time of passengers grouped by request time (bins of `width` ticks), pooled over seeds."""
    edges = np.arange(0, duration + width, width)
    sums, counts = np.zeros(len(edges) - 1), np.zeros(len(edges) - 1)
    for seed in range(seeds):
        result = run(building(name, dwell), generate("up-peak", 30, rate, duration, seed), name.split()[0])
        times = [p.request.time for p in result.passengers]
        idx = np.clip(np.digitize(times, edges) - 1, 0, len(sums) - 1)
        np.add.at(sums, idx, [p.total_time for p in result.passengers])
        np.add.at(counts, idx, 1)
    return edges[:-1] + width / 2, sums / counts


def overload():
    fig, ax = plt.subplots()
    fig.subplots_adjust(top=0.84, right=0.84)
    for name in ("zone", "etd", "etd + express"):
        x, y = binned_total(name, 0.8, dwell=1)
        ax.plot(x, y, color=COLOR[name], marker="o", ms=7, label=LABEL[name])
        nudge = {"zone": 6, "etd + express": -6}.get(name, 0)
        ax.annotate(LABEL[name], (x[-1], y[-1]), xytext=(10, nudge), textcoords="offset points", va="center", color=INK)
    ax.set(xlabel="request time (tick)", ylabel="mean total time, ticks", ylim=(0, None))
    ax.legend(loc="upper left")
    save(fig, "overload.png", "When stops cost time, ETD's queue grows; an express bank closes the gap",
         ETD_NOTE + "Up-peak, 0.8 passengers/tick, dwell = 1: mean total time by arrival time (60-tick bins, 3 seeds)")


def load_sweep():
    rates = [0.2, 0.4, 0.6, 0.8, 1.0]
    fig, axes = plt.subplots(1, 2, sharey=True)
    fig.subplots_adjust(top=0.80, bottom=0.12, wspace=0.08)
    for ax, dwell in zip(axes, (0, 1)):
        for name in ("zone", "etd", "etd + express"):
            means = []
            for rate in rates:
                totals = [p.total_time for seed in range(3) for p in
                          run(building(name, dwell), generate("up-peak", 30, rate, 600, seed),
                              name.split()[0]).passengers]
                means.append(np.mean(totals))
            ax.plot(rates, means, color=COLOR[name], marker="o", ms=9, label=LABEL[name])
        ax.set_title(f"dwell = {dwell}", loc="left", color=INK)
        ax.set(xlabel="arrival rate (passengers per tick)", xticks=rates)
    axes[0].set(ylabel="mean total time, ticks", ylim=(0, None))
    axes[0].legend(loc="upper left")
    save(fig, "load_sweep.png", "ETD leads until the building nears saturation, then degrades faster than zone",
         ETD_NOTE + "Up-peak, 30 floors, 4 cars; 3 seeds x 600 ticks per point")


def fairness():
    rows = read_rows("fairness_dwell1")
    fig, axes = plt.subplots(1, 2)
    fig.subplots_adjust(top=0.80, bottom=0.17, wspace=0.18)
    offsets = (-0.2, 0, 0.2)
    for ax, (col, label) in zip(axes, (("total_mean", "mean total time"), ("total_max", "worst total time"))):
        for d, dx in zip(("etd-p1", "etd-p2", "etd-p4"), offsets):
            vals = [next(r[col] for r in rows if r["scenario"] == s and r["dispatcher"] == d) for s in SCENARIOS]
            ax.bar(np.arange(len(SCENARIOS)) + dx, vals, width=0.19, color=COLOR[d], label=LABEL[d])
        ax.set_xticks(range(len(SCENARIOS)), SCENARIOS)
        ax.set_title(label + ", ticks", loc="left", color=INK)
        ax.grid(axis="x", visible=False)
    axes[0].legend(loc="upper center", bbox_to_anchor=(1.09, -0.09), ncol=3)
    save(fig, "fairness.png", "Higher p cuts the worst case everywhere; the mean moves only in up-peak",
         ETD_NOTE + "ETD with cost = total_time^p, 0.8 passengers/tick, dwell = 1, 10 seeds x 1200 ticks")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    charts = [algorithms, overload, load_sweep, fairness]
    only = set(sys.argv[1:])
    for chart in charts:
        if not only or chart.__name__ in only:
            chart()
