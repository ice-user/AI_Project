"""Auto-adjust: move the player up or down a level so they win roughly half the time.

Done when: a test player who always loses gets moved down, one who always wins gets moved up.
"""

from __future__ import annotations


def next_level(current_level: int, recent_results: list[float]) -> int:
    """recent_results: newest last, 1 = player won, 0.5 = draw, 0 = lost."""
    # TODO(P3)
    raise NotImplementedError
