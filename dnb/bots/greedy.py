"""Greedy bot (owner: Person 1).

Takes a box whenever it can; otherwise avoids moves that leave a box with 3 sides
(giving the opponent a free box); otherwise plays randomly.
"""

from __future__ import annotations

import random

from dnb.bots.base import Bot
from dnb.engine import GameState


class GreedyBot(Bot):
    name = "greedy"

    def __init__(self, seed: int | None = None, randomness: float = 0.0) -> None:
        # `randomness` = chance of playing a random move instead (Person 3 uses it for Easy levels).
        self.rng = random.Random(seed)
        self.randomness = randomness

    def evaluate_moves(self, state: GameState) -> dict[int, float]:
        # TODO(P1): +score for moves that complete boxes, -score for moves that leave a 3-sided box.
        # Tip: state.boxes_completed_by(move) and state.sides(box) do most of the work.
        raise NotImplementedError
