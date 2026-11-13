"""Automatically adjust difficulty based on recent player performance."""

from __future__ import annotations

import math

MIN_LEVEL = 1
MAX_LEVEL = 5

WINDOW_SIZE = 5
MIN_GAMES = 3

WIN_THRESHOLD = 0.70
LOSS_THRESHOLD = 0.30


def next_level(current_level: int, recent_results: list[float]) -> int:
    """Return the next difficulty level based on recent game results.

    Results:
        1.0 = player won
        0.5 = draw
        0.0 = player lost

    Uses the last five results. At least three results are
    required before changing difficulty.
    """

    if isinstance(current_level, bool) or not isinstance(current_level, int):
        raise ValueError("Current level must be an integer.")

    if not MIN_LEVEL <= current_level <= MAX_LEVEL:
        raise ValueError("Current level must be between 1 and 5.")

    if any(not math.isfinite(result) or not 0.0 <= result <= 1.0 for result in recent_results):
        raise ValueError("Game results must be between 0 and 1.")

    # Not enough games to make a reliable adjustment.
    if len(recent_results) < MIN_GAMES:
        return current_level

    # Consider only the most recent five games.
    recent = recent_results[-WINDOW_SIZE:]

    average_score = sum(recent) / len(recent)

    # Player is consistently winning: increase difficulty.
    if average_score >= WIN_THRESHOLD - 1e-9:
        return min(current_level + 1, MAX_LEVEL)

    if average_score <= LOSS_THRESHOLD + 1e-9:
        return max(current_level - 1, MIN_LEVEL)

    # Performance is balanced: maintain difficulty.
    return current_level
