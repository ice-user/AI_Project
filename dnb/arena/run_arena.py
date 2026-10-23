"""Bot arena (owner: Person 2): every bot plays every other bot, producing a win-rate table.

Run:  uv run python -m dnb.arena.run_arena
"""

from __future__ import annotations

from dnb.arena.match import play_game
from dnb.bots import make_bot

# TODO(P2): extend with greedy / minimax depths / montecarlo sims once they exist.
DEFAULT_SPECS = ["random", "random:seed=1"]


def run_arena(specs: list[str], games_per_pair: int = 100, rows: int = 3, cols: int = 3):
    # TODO(P2): swap who moves first each game, collect win rates + think time,
    # write results/arena.csv, and draw charts with matplotlib (dnb/arena/charts.py).
    for i, a in enumerate(specs):
        for b in specs[i + 1 :]:
            wins = [0, 0]
            for _ in range(games_per_pair):
                rec = play_game(make_bot(a), make_bot(b), rows, cols)
                if rec.winner is not None:
                    wins[rec.winner] += 1
            print(f"{a:>20} vs {b:<20} {wins[0]:>4} - {wins[1]:<4}")


if __name__ == "__main__":
    run_arena(DEFAULT_SPECS, games_per_pair=20)
