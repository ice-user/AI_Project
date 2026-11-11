"""Difficulty levels = bot specs (see dnb/bots/registry.py).

TODO(P3): tune these using the arena results so each level is clearly stronger than the last.
These specs only work once Persons 1 and 2 implement the bots; until then play "random".
"""

from __future__ import annotations

LEVELS: dict[int, dict[str, str]] = {
    1: {"name": "Beginner", "bot": "greedy:randomness=0.5"},
    2: {"name": "Easy", "bot": "greedy"},
    3: {"name": "Medium", "bot": "minimax:depth=2"},
    4: {"name": "Hard", "bot": "minimax:depth=4"},
    5: {"name": "Expert", "bot": "montecarlo:sims=2000,greedy_playouts=true"},
}


def bot_spec_for_level(level: int) -> str:
    """Return the bot specification for a difficulty level."""

    if isinstance(level, bool) or not isinstance(level, int):
        raise ValueError("Difficulty level must be an integer.")

    if level not in LEVELS:
        raise ValueError("Difficulty level must be between 1 and 5.")

    return LEVELS[level]["bot"]