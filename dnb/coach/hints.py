"""Hint button + danger highlight."""

from __future__ import annotations

from dnb.bots.base import MoveResult
from dnb.engine import GameState

HINT_BOT = "random"  # TODO(P4): switch to the strongest bot once the arena says which one it is


def hint(state: GameState) -> MoveResult:
    """Best move for the player to move, according to HINT_BOT."""
    # TODO(P4): make_bot(HINT_BOT).choose_move(state)
    raise NotImplementedError


def dangerous_moves(state: GameState) -> list[int]:
    """Legal moves that would leave a box with 3 sides (a free box for the opponent)."""
    # TODO(P4)
    raise NotImplementedError
