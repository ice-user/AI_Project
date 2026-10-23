"""Minimax bot with alpha-beta pruning (owner: Person 1).

Careful: because of the extra-turn rule, the player to move does NOT simply alternate.
Decide max/min from `state.current_player`, never from depth parity.
"""

from __future__ import annotations

from dnb.bots.base import Bot
from dnb.engine import GameState


class MinimaxBot(Bot):
    name = "minimax"

    def __init__(self, depth: int = 3) -> None:
        self.depth = depth

    def evaluate_moves(self, state: GameState) -> dict[int, float]:
        # TODO(P1): alpha-beta search to self.depth; leaf score = (my boxes - their boxes) / total.
        raise NotImplementedError
