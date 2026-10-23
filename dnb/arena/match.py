"""Play one full bot-vs-bot game. Used by the arena, tests and difficulty calibration."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from dnb.bots.base import Bot
from dnb.engine import GameState


@dataclass
class GameRecord:
    rows: int
    cols: int
    moves: list[tuple[int, int]] = field(default_factory=list)  # (player, edge)
    scores: tuple[int, int] = (0, 0)
    winner: int | None = None  # None = draw
    think_time: list[float] = field(default_factory=lambda: [0.0, 0.0])  # seconds per player


def play_game(bot0: Bot, bot1: Bot, rows: int = 3, cols: int = 3) -> GameRecord:
    state = GameState.new(rows, cols)
    bots = (bot0, bot1)
    record = GameRecord(rows=rows, cols=cols)
    while not state.is_over():
        player = state.current_player
        start = time.perf_counter()
        result = bots[player].choose_move(state)
        record.think_time[player] += time.perf_counter() - start
        record.moves.append((player, result.move))
        state = state.apply(result.move)
    record.scores = state.scores
    record.winner = state.winner()
    return record
