"""Elo rating for players (and, optionally, for each bot level)."""

from __future__ import annotations

DEFAULT_RATING = 1000.0
K_FACTOR = 32.0


def expected_score(rating_a: float, rating_b: float) -> float:
    """Probability that A beats B."""
    # TODO(P3)
    raise NotImplementedError


def update(rating_a: float, rating_b: float, score_a: float) -> tuple[float, float]:
    """score_a: 1 = A won, 0.5 = draw, 0 = A lost. Returns new (rating_a, rating_b)."""
    # TODO(P3)
    raise NotImplementedError
