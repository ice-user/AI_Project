
"""Elo rating for players (and, optionally, for each bot level)."""

from __future__ import annotations

import math

DEFAULT_RATING = 1000.0
K_FACTOR = 32.0


def expected_score(rating_a: float, rating_b: float) -> float:
    """Return the probability that player A beats player B."""
    if not math.isfinite(rating_a) or not math.isfinite(rating_b):
        raise ValueError("Ratings must be finite numbers.")

    difference = (rating_b - rating_a) / 400.0

    # Calculate the logistic formula without overflowing for
    # very large differences in ratings.
    if difference >= 0:
        power = 10 ** (-difference)
        return power / (1 + power)

    power = 10 ** difference
    return 1 / (1 + power)


def update(
    rating_a: float,
    rating_b: float,
    score_a: float,
) -> tuple[float, float]:
    """Update both ratings after a game.

    score_a:
        1.0 = A won
        0.5 = draw
        0.0 = A lost

    Returns:
        A tuple containing (new_rating_a, new_rating_b).
    """
    if not math.isfinite(score_a) or not 0 <= score_a <= 1:
        raise ValueError("score_a must be between 0 and 1.")

    expected_a = expected_score(rating_a, rating_b)

    change = K_FACTOR * (score_a - expected_a)

    new_rating_a = rating_a + change
    new_rating_b = rating_b - change

    return new_rating_a, new_rating_b
