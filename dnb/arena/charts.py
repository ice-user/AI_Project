"""Result charts for the report (owner: Person 2). Needs the `arena` extra (matplotlib).

* ``plot_arena``: win-rate matrix, plus overall score and think time per bot.
* ``plot_sweep``: Monte Carlo strength and think time as `sims` grows (see dnb/arena/sweep.py).

Redraw arena charts from a saved CSV, without replaying any games:
    uv run python -m dnb.arena.charts results/arena_3x3_pairs.csv [--out docs/report]

Colours come from one fixed palette so every chart in the report looks the same:
blue = random playouts / "good", orange = greedy playouts, and a blue <-> red diverging scale
with a grey midpoint for win rates (blue: row bot wins, red: row bot loses).
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib

matplotlib.use("Agg")  # no window, works on CI and over SSH

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.ticker import (  # noqa: E402
    FuncFormatter,
    LogLocator,
    NullLocator,
    PercentFormatter,
)

if TYPE_CHECKING:
    from dnb.arena.run_arena import ArenaResult
    from dnb.arena.sweep import SweepPoint

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
DIVERGING = LinearSegmentedColormap.from_list(
    "winrate", ["#e34948", "#f3a6a2", "#f0efec", "#86b6ef", "#1c5cab"]
)

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 10,
        "text.color": INK,
        "axes.labelcolor": INK_2,
        "axes.edgecolor": AXIS,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelcolor": INK_2,
        "ytick.labelcolor": INK_2,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "legend.frameon": False,
    }
)


def _ms(value: float, _pos: object = None) -> str:
    if value >= 1000:
        return f"{value / 1000:g} s"
    return f"{value:g} ms"


def plot_arena(result: ArenaResult, out_dir: str | Path = "results") -> list[Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tag = f"arena_{result.rows}x{result.cols}"
    return [
        _plot_matrix(result, out / f"{tag}_matrix.png"),
        _plot_strength(result, out / f"{tag}_strength.png"),
    ]


def _plot_matrix(result: ArenaResult, path: Path) -> Path:
    specs = result.specs
    n = len(specs)
    grid = [[result.score(a, b) if a != b else float("nan") for b in specs] for a in specs]
    games = result.pairs[0].games if result.pairs else 0

    size = 1.0 + 0.85 * n
    fig, ax = plt.subplots(figsize=(size + 3.2, size))
    image = ax.imshow(grid, cmap=DIVERGING, vmin=0, vmax=1)
    ax.set_xticks(range(n), [f"#{i + 1}" for i in range(n)])
    ax.set_yticks(range(n), [f"#{i + 1}  {s}" for i, s in enumerate(specs)])
    ax.tick_params(length=0)
    ax.xaxis.tick_top()
    for spine in ax.spines.values():
        spine.set_visible(False)
    # 2px surface gap between cells
    ax.set_xticks([x - 0.5 for x in range(1, n)], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, n)], minor=True)
    ax.grid(which="minor", color=SURFACE, linewidth=2)
    ax.tick_params(which="minor", length=0)
    for i in range(n):
        for j in range(n):
            value = grid[i][j]
            if i == j:
                ax.text(j, i, "—", ha="center", va="center", color=MUTED)
                continue
            strong = abs(value - 0.5) > 0.32
            ax.text(
                j,
                i,
                f"{100 * value:.0f}%",
                ha="center",
                va="center",
                fontsize=9,
                color="#ffffff" if strong else INK,
            )
    bar = fig.colorbar(image, ax=ax, fraction=0.04, pad=0.03)
    bar.outline.set_visible(False)
    bar.ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    bar.ax.tick_params(colors=MUTED, labelcolor=INK_2, length=0)
    ax.set_title(
        f"Win rate of row bot vs column bot · {result.rows}×{result.cols} board, "
        f"{games} games per pair",
        pad=28,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    return path


def _plot_strength(result: ArenaResult, path: Path) -> Path:
    summaries = sorted(result.summaries(), key=lambda s: s.score)
    labels = [s.spec for s in summaries]
    y = range(len(summaries))

    fig, (left, right) = plt.subplots(
        1, 2, sharey=True, figsize=(10, 0.9 + 0.45 * len(summaries)), width_ratios=[3, 2.4]
    )
    left.barh(y, [s.score for s in summaries], color=BLUE, height=0.6)
    left.set_yticks(y, labels)
    left.set_xlim(0, 1)
    left.xaxis.set_major_formatter(PercentFormatter(1.0))
    left.axvline(0.5, color=AXIS, linewidth=1, linestyle=(0, (3, 3)))
    left.set_title("Overall win rate vs all other bots")
    for i, s in enumerate(summaries):
        left.text(s.score + 0.01, i, f"{100 * s.score:.0f}%", va="center", color=INK_2, fontsize=9)

    times = [max(s.ms_per_move, 1e-3) for s in summaries]
    right.barh(y, times, color=BLUE, height=0.6)
    right.set_xscale("log")
    right.xaxis.set_major_formatter(FuncFormatter(_ms))
    right.set_title("Think time per move (log scale)")
    right.xaxis.set_major_locator(LogLocator(base=100))
    right.xaxis.set_minor_locator(NullLocator())
    for i, t in enumerate(times):
        right.text(
            t * 1.15, i, _ms(round(t, 2 if t < 1 else 0)), va="center", color=INK_2, fontsize=9
        )
    right.set_xlim(right=max(times) * 8)

    for ax in (left, right):
        ax.grid(axis="x")
        ax.set_axisbelow(True)
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
    fig.suptitle(
        f"Strength and cost per bot · {result.rows}×{result.cols} board",
        x=0.01,
        ha="left",
        fontweight="bold",
        fontsize=13,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    return path


def plot_sweep(
    points: Sequence[SweepPoint], opponent: str, rows: int, cols: int, path: str | Path
) -> Path:
    """Two panels sharing the x axis (sims): win rate vs `opponent`, and think time."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    series = [("random playouts", False, BLUE), ("greedy playouts", True, ORANGE)]

    fig, (top, bottom) = plt.subplots(2, 1, sharex=True, figsize=(8, 7), height_ratios=[3, 2])
    for label, greedy, colour in series:
        pts = sorted((p for p in points if p.greedy_playouts == greedy), key=lambda p: p.sims)
        if not pts:
            continue
        xs = [p.sims for p in pts]
        style = {"color": colour, "linewidth": 2, "marker": "o", "markersize": 6}
        style["markeredgecolor"] = SURFACE
        top.plot(xs, [p.score for p in pts], label=label, **style)
        bottom.plot(xs, [p.ms_per_move for p in pts], label=label, **style)
        top.annotate(
            label,
            (xs[-1], pts[-1].score),
            xytext=(8, 0),
            textcoords="offset points",
            va="center",
            color=INK_2,
        )

    top.axhline(0.5, color=AXIS, linewidth=1, linestyle=(0, (3, 3)))
    top.set_ylim(0, 1)
    top.yaxis.set_major_formatter(PercentFormatter(1.0))
    top.set_ylabel(f"win rate vs {opponent}")
    top.set_title(f"Monte Carlo bot: more simulations, stronger play · {rows}×{cols} board")
    top.legend(loc="center right")

    bottom.set_yscale("log")
    bottom.yaxis.set_major_formatter(FuncFormatter(_ms))
    bottom.set_ylabel("think time per move")
    bottom.set_xscale("log")
    bottom.set_xlabel("simulations per decision (sims)")
    xs = sorted({p.sims for p in points})
    bottom.set_xticks(xs, [f"{x:g}" for x in xs])
    bottom.minorticks_off()

    for ax in (top, bottom):
        ax.grid(axis="y")
        ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    return path


def main(argv: Sequence[str] | None = None) -> None:
    import argparse

    from dnb.arena.run_arena import read_csv

    ap = argparse.ArgumentParser(description="Redraw arena charts from a pairs CSV.")
    ap.add_argument("pairs_csv")
    ap.add_argument("--out", default=None, help="folder for the PNGs (default: next to the CSV)")
    args = ap.parse_args(argv)
    out = args.out or Path(args.pairs_csv).parent
    for path in plot_arena(read_csv(args.pairs_csv), out):
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
