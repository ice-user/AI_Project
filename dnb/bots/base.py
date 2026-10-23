"""The Bot interface every bot implements.

CONTRACT (see docs/ARCHITECTURE.md): frozen. Changing it needs a whole-team PR.

Score convention
----------------
Every score is in [-1.0, 1.0], from the point of view of the player to move
(`state.current_player`), higher is better:

* minimax:      (my boxes - opponent boxes) / total boxes in the final position it reaches
* monte carlo:  2 * win_rate - 1
* random:       0.0 for every move

Keeping one scale lets difficulty (Person 3) and review (Person 4) compare bots fairly.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from dnb.engine import GameState


@dataclass(frozen=True)
class MoveResult:
    move: int
    score: float  # in [-1, 1], higher is better for the player to move
    info: dict[str, Any] = field(default_factory=dict)  # e.g. {"depth": 3, "nodes": 1234}


class Bot(ABC):
    """Give it the board, get back a move and a score."""

    name: str = "bot"

    @abstractmethod
    def evaluate_moves(self, state: GameState) -> dict[int, float]:
        """Score every legal move. Needed by hints and move review."""

    def choose_move(self, state: GameState) -> MoveResult:
        """Pick the best move. Override when the bot can do it cheaper than scoring everything."""
        scores = self.evaluate_moves(state)
        move = max(scores, key=scores.__getitem__)
        return MoveResult(move=move, score=scores[move])
