"""Monte Carlo strength sweep (owner: Person 2): how win rate and think time grow with `sims`.

Plays MonteCarloBot at several `sims` values, with random and with greedy playouts, against one
opponent (greedy by default). Useful for the report and for Person 3's difficulty levels.

Run:
    uv run python -m dnb.arena.sweep
    uv run python -m dnb.arena.sweep --sims 50 200 1000 --games 40 --opponent "minimax:depth=3"
"""

from __future__ import annotations

import argparse
import csv
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from dnb.arena.run_arena import run_arena

DEFAULT_SIMS = [25, 50, 100, 200, 500, 1000, 2000]


@dataclass(frozen=True)
class SweepPoint:
    sims: int
    greedy_playouts: bool
    games: int
    score: float  # win rate vs the opponent, draw = half
    ms_per_move: float


def run_sweep(
    sims_values: Sequence[int] = DEFAULT_SIMS,
    opponent: str = "greedy",
    games: int = 100,
    rows: int = 3,
    cols: int = 3,
    seed: int = 0,
    workers: int | None = 1,
) -> list[SweepPoint]:
    points = []
    for greedy in (False, True):
        for sims in sims_values:
            spec = f"montecarlo:sims={sims},greedy_playouts={str(greedy).lower()}"
            result = run_arena([spec, opponent], games, rows, cols, seed, workers)
            pair = result.pairs[0]
            points.append(SweepPoint(sims, greedy, pair.games, pair.score_a, pair.ms_per_move_a))
            print(
                f"  sims={sims:<6} greedy_playouts={greedy!s:<5}  "
                f"win rate {100 * pair.score_a:5.1f}%  {pair.ms_per_move_a:8.2f} ms/move"
            )
    return points


def write_csv(points: Sequence[SweepPoint], path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sims", "greedy_playouts", "games", "score", "ms_per_move"])
        for p in points:
            w.writerow(
                [p.sims, p.greedy_playouts, p.games, f"{p.score:.4f}", f"{p.ms_per_move:.3f}"]
            )
    return path


def main(argv: Sequence[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--sims", nargs="+", type=int, default=DEFAULT_SIMS)
    ap.add_argument("--opponent", default="greedy")
    ap.add_argument("--games", type=int, default=100)
    ap.add_argument("--rows", type=int, default=3)
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--workers", type=int, default=None, help="processes (default: all CPUs)")
    ap.add_argument("--out", default="results")
    args = ap.parse_args(argv)

    print(f"Monte Carlo vs {args.opponent} on {args.rows}x{args.cols}, {args.games} games each")
    points = run_sweep(
        args.sims, args.opponent, args.games, args.rows, args.cols, args.seed, args.workers
    )
    tag = f"sweep_{args.rows}x{args.cols}"
    print(f"Wrote {write_csv(points, Path(args.out) / f'{tag}.csv')}")
    from dnb.arena.charts import plot_sweep

    path = plot_sweep(points, args.opponent, args.rows, args.cols, Path(args.out) / f"{tag}.png")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
