"""Random bot: the weakest baseline (owner: Person 1)."""

from __future__ import annotations

import random

from dnb.bots.base import Bot, MoveResult
from dnb.engine import GameState


class RandomBot(Bot):
    name = "random"

    def __init__(self, seed: int | None = None) -> None:
        self.rng = random.Random(seed)

    def evaluate_moves(self, state: GameState) -> dict[int, float]:
        return {m: 0.0 for m in state.legal_moves()}

    def choose_move(self, state: GameState) -> MoveResult:
        return MoveResult(move=self.rng.choice(state.legal_moves()), score=0.0)
