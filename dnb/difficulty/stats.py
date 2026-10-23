"""Player stats for the profile screen, computed from saved games (dnb/server/db.py)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PlayerStats:
    games_played: int
    win_rate: float
    boxes_given_away_per_game: float  # moves that left a 3-sided box for the bot
    rating: float
    level: int


def compute_stats(player_id: str) -> PlayerStats:
    # TODO(P3): read the games/moves tables via dnb.server.db
    raise NotImplementedError
