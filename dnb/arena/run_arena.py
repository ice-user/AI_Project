"""Bot arena (owner: Person 2): every bot plays every other bot, producing a win-rate table.

Run:
    uv run python -m dnb.arena.run_arena                       # default bots, 100 games per pair
    uv run python -m dnb.arena.run_arena --games 20 --rows 4 --cols 4
    uv run python -m dnb.arena.run_arena --specs random greedy "montecarlo:sims=500"
    uv run python -m dnb.arena.run_arena --charts              # also draw PNG charts

Fairness: the two bots swap who moves first every game, and every game gets its own seed, so
a run is reproducible (same --seed, same results) without two seeded bots replaying one game.

Output (in --out, default ``results/``, which git ignores):
    arena_<R>x<C>_pairs.csv   one row per pair of bots
    arena_<R>x<C>_bots.csv    one row per bot, totals over all its games
Copy the final charts you want in the report to docs/report/.
"""

from __future__ import annotations

import argparse
import csv
import inspect
import os
import random
from collections.abc import Callable, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from dnb.arena.match import play_game
from dnb.bots import BOTS, Bot, make_bot, parse_spec

DEFAULT_SPECS = [
    "random",
    "greedy",
    "minimax:depth=2",
    "minimax:depth=4",
    "montecarlo:sims=500",
    "montecarlo:sims=500,greedy_playouts=true",
    "montecarlo:sims=2000,greedy_playouts=true",
]


# ---------------------------------------------------------------------------- results


@dataclass
class PairResult:
    """Results of `a` vs `b` over many games. Counts are from `a`'s side unless named `_b`."""

    a: str
    b: str
    games: int = 0
    wins_a: int = 0
    wins_b: int = 0
    draws: int = 0
    boxes_a: int = 0
    boxes_b: int = 0
    time_a: float = 0.0  # total seconds thinking
    time_b: float = 0.0
    moves_a: int = 0
    moves_b: int = 0

    @property
    def score_a(self) -> float:
        """Win rate of `a`, counting a draw as half a win."""
        return (self.wins_a + self.draws / 2) / self.games if self.games else 0.0

    @property
    def score_b(self) -> float:
        return 1.0 - self.score_a if self.games else 0.0

    @property
    def ms_per_move_a(self) -> float:
        return 1000 * self.time_a / self.moves_a if self.moves_a else 0.0

    @property
    def ms_per_move_b(self) -> float:
        return 1000 * self.time_b / self.moves_b if self.moves_b else 0.0


@dataclass
class BotSummary:
    """One bot's totals over every game it played in the arena."""

    spec: str
    games: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    time: float = 0.0
    moves: int = 0

    @property
    def score(self) -> float:
        return (self.wins + self.draws / 2) / self.games if self.games else 0.0

    @property
    def ms_per_move(self) -> float:
        return 1000 * self.time / self.moves if self.moves else 0.0


@dataclass
class ArenaResult:
    specs: list[str]
    rows: int
    cols: int
    pairs: list[PairResult]

    def pair(self, a: str, b: str) -> PairResult:
        for p in self.pairs:
            if (p.a, p.b) == (a, b):
                return p
        raise KeyError((a, b))

    def score(self, a: str, b: str) -> float:
        """Win rate of `a` against `b` (draw = half), in either order."""
        for p in self.pairs:
            if (p.a, p.b) == (a, b):
                return p.score_a
            if (p.a, p.b) == (b, a):
                return p.score_b
        raise KeyError((a, b))

    def summaries(self) -> list[BotSummary]:
        out = {s: BotSummary(s) for s in self.specs}
        for p in self.pairs:
            sa, sb = out[p.a], out[p.b]
            sa.games += p.games
            sb.games += p.games
            sa.wins += p.wins_a
            sa.losses += p.wins_b
            sb.wins += p.wins_b
            sb.losses += p.wins_a
            sa.draws += p.draws
            sb.draws += p.draws
            sa.time += p.time_a
            sb.time += p.time_b
            sa.moves += p.moves_a
            sb.moves += p.moves_b
        return list(out.values())


# ---------------------------------------------------------------------------- playing


def build_bot(spec: str, seed: int) -> Bot:
    """make_bot(spec), plus `seed` for bots that take one and whose spec does not set it."""
    name, kwargs = parse_spec(spec)
    cls = BOTS.get(name)
    if cls is not None and "seed" not in kwargs:
        if "seed" in inspect.signature(cls.__init__).parameters:
            spec = f"{spec}{',' if ':' in spec else ':'}seed={seed}"
    return make_bot(spec)


def _play_one(job: tuple[int, str, str, bool, int, int, int]) -> tuple:
    """Play one game of pair `index`. Top level so worker processes can run it."""
    index, a, b, a_first, rows, cols, seed = job
    bot_a, bot_b = build_bot(a, seed), build_bot(b, seed + 1)
    if a_first:
        rec = play_game(bot_a, bot_b, rows, cols)
        pa = 0
    else:
        rec = play_game(bot_b, bot_a, rows, cols)
        pa = 1
    moves_a = sum(1 for player, _ in rec.moves if player == pa)
    return (
        index,
        rec.winner,
        pa,
        rec.scores[pa],
        rec.scores[1 - pa],
        rec.think_time[pa],
        rec.think_time[1 - pa],
        moves_a,
        len(rec.moves) - moves_a,
    )


def _add_game(p: PairResult, outcome: tuple) -> None:
    _, winner, pa, boxes_a, boxes_b, time_a, time_b, moves_a, moves_b = outcome
    p.games += 1
    if winner is None:
        p.draws += 1
    elif winner == pa:
        p.wins_a += 1
    else:
        p.wins_b += 1
    p.boxes_a += boxes_a
    p.boxes_b += boxes_b
    p.time_a += time_a
    p.time_b += time_b
    p.moves_a += moves_a
    p.moves_b += moves_b


def run_arena(
    specs: Sequence[str],
    games_per_pair: int = 100,
    rows: int = 3,
    cols: int = 3,
    seed: int = 0,
    workers: int | None = 1,
    progress: Callable[[int, int], None] | None = None,
) -> ArenaResult:
    """Play every pair of `specs` `games_per_pair` times, alternating who starts.

    `workers` > 1 plays games in parallel processes (None = one per CPU). Think time is
    measured inside each game, so it stays comparable whatever the number of workers.
    """
    specs = list(dict.fromkeys(specs))  # drop duplicates, keep order
    for spec in specs:
        make_bot(spec)  # fail fast on a typo before starting a long run
    pairs = [PairResult(a, b) for i, a in enumerate(specs) for b in specs[i + 1 :]]
    rng = random.Random(seed)
    jobs = [
        (k, p.a, p.b, g % 2 == 0, rows, cols, rng.randrange(2**31))
        for k, p in enumerate(pairs)
        for g in range(games_per_pair)
    ]
    done = 0
    if workers == 1:
        outcomes = map(_play_one, jobs)
        pool = None
    else:
        pool = ProcessPoolExecutor(max_workers=workers or os.cpu_count())
        outcomes = pool.map(_play_one, jobs, chunksize=max(1, len(jobs) // 200))
    try:
        for outcome in outcomes:
            _add_game(pairs[outcome[0]], outcome)
            done += 1
            if progress:
                progress(done, len(jobs))
    finally:
        if pool:
            pool.shutdown()
    return ArenaResult(specs=specs, rows=rows, cols=cols, pairs=pairs)


# ---------------------------------------------------------------------------- output


def write_csv(result: ArenaResult, out_dir: str | Path = "results") -> tuple[Path, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tag = f"arena_{result.rows}x{result.cols}"
    pairs_path, bots_path = out / f"{tag}_pairs.csv", out / f"{tag}_bots.csv"
    with pairs_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            ["bot_a", "bot_b", "rows", "cols", "games", "wins_a", "wins_b", "draws"]
            + ["score_a", "avg_margin_a", "ms_per_move_a", "ms_per_move_b"]
            + ["boxes_a", "boxes_b", "moves_a", "moves_b", "time_a_s", "time_b_s"]
        )
        for p in result.pairs:
            margin = (p.boxes_a - p.boxes_b) / p.games if p.games else 0.0
            w.writerow(
                [p.a, p.b, result.rows, result.cols, p.games, p.wins_a, p.wins_b, p.draws]
                + [f"{p.score_a:.4f}", f"{margin:.3f}"]
                + [f"{p.ms_per_move_a:.3f}", f"{p.ms_per_move_b:.3f}"]
                + [p.boxes_a, p.boxes_b, p.moves_a, p.moves_b, f"{p.time_a:.6f}", f"{p.time_b:.6f}"]
            )
    with bots_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            ["bot", "rows", "cols", "games", "wins", "losses", "draws", "score"] + ["ms_per_move"]
        )
        for s in result.summaries():
            w.writerow(
                [s.spec, result.rows, result.cols, s.games, s.wins, s.losses, s.draws]
                + [f"{s.score:.4f}", f"{s.ms_per_move:.3f}"]
            )
    return pairs_path, bots_path


def read_csv(pairs_path: str | Path) -> ArenaResult:
    """Load an ``arena_*_pairs.csv`` back, e.g. to redraw charts without replaying games."""
    with Path(pairs_path).open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{pairs_path} has no results")
    pairs, specs = [], []
    for r in rows:
        ints = {k: int(r[k]) for k in ("games", "wins_a", "wins_b", "draws")}
        ints |= {k: int(r[k]) for k in ("boxes_a", "boxes_b", "moves_a", "moves_b")}
        pairs.append(
            PairResult(
                r["bot_a"],
                r["bot_b"],
                **ints,
                time_a=float(r["time_a_s"]),
                time_b=float(r["time_b_s"]),
            )
        )
        specs += [r["bot_a"], r["bot_b"]]
    return ArenaResult(
        list(dict.fromkeys(specs)), int(rows[0]["rows"]), int(rows[0]["cols"]), pairs
    )


def format_table(result: ArenaResult) -> str:
    """Matrix of win rates: the cell in row A, column B is A's win rate against B."""
    specs = result.specs
    width = max(len(s) for s in specs)
    short = [f"#{i + 1}" for i in range(len(specs))]
    lines = [" " * (width + 5) + "".join(f"{s:>7}" for s in short) + "   overall   ms/move"]
    summaries = {s.spec: s for s in result.summaries()}
    for i, a in enumerate(specs):
        cells = "".join(
            f"{'—':>7}" if a == b else f"{100 * result.score(a, b):>6.0f}%" for b in specs
        )
        s = summaries[a]
        lines.append(
            f"#{i + 1:<3} {a:<{width}}{cells}   {100 * s.score:>6.1f}%  {s.ms_per_move:>8.2f}"
        )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--specs", nargs="+", default=DEFAULT_SPECS, help="bot specs to compare")
    ap.add_argument("--games", type=int, default=100, help="games per pair (default 100)")
    ap.add_argument("--rows", type=int, default=3)
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--workers", type=int, default=None, help="processes (default: all CPUs)")
    ap.add_argument("--out", default="results", help="output folder (default results/)")
    ap.add_argument("--charts", action="store_true", help="also draw PNG charts (matplotlib)")
    args = ap.parse_args(argv)

    def progress(done: int, total: int) -> None:
        if done == total or done % max(1, total // 20) == 0:
            print(f"\r  {done}/{total} games", end="", flush=True)

    n = len(dict.fromkeys(args.specs))
    print(f"{n} bots, {n * (n - 1) // 2} pairs x {args.games} games on {args.rows}x{args.cols}")
    result = run_arena(
        args.specs, args.games, args.rows, args.cols, args.seed, args.workers, progress
    )
    print("\n\nWin rate of the row bot against the column bot (draw = half a win):\n")
    print(format_table(result))
    pairs_path, bots_path = write_csv(result, args.out)
    print(f"\nWrote {pairs_path} and {bots_path}")
    if args.charts:
        from dnb.arena.charts import plot_arena

        for path in plot_arena(result, args.out):
            print(f"Wrote {path}")


if __name__ == "__main__":
    main()
