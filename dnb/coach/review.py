"""Post-game review: label each human move Good / Okay / Mistake vs. the bot's best move."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Label = Literal["good", "okay", "mistake"]


@dataclass
class MoveReview:
    ply: int  # index into the game's move list
    move: int
    best_move: int
    score: float  # score of the played move, [-1, 1]
    best_score: float
    label: Label


def review_game(rows: int, cols: int, moves: list[tuple[int, int]], human: int) -> list[MoveReview]:
    """moves: (player, edge) in order. Reviews only the human's moves."""
    # TODO(P4): replay with GameState, call bot.evaluate_moves() before each human move,
    # label by the gap between best_score and score.
    raise NotImplementedError
