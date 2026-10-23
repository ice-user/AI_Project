"""Monte Carlo bot (owner: Person 2).

For each legal move, play `sims` quick games to the end and pick the move that wins most.
Stretch goal: full MCTS (UCT) in a separate class, same interface.
"""

from __future__ import annotations

import random

from dnb.bots.base import Bot
from dnb.engine import GameState


class MonteCarloBot(Bot):
    name = "montecarlo"

    def __init__(self, sims: int = 200, greedy_playouts: bool = False, seed: int | None = None):
        self.sims = sims  # total simulations per move decision; more = stronger
        self.greedy_playouts = greedy_playouts  # follow the greedy rule in playouts
        self.rng = random.Random(seed)

    def evaluate_moves(self, state: GameState) -> dict[int, float]:
        # TODO(P2): run playouts per move, return {move: 2 * win_rate - 1}.
        raise NotImplementedError
