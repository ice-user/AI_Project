"""Player stats for the profile screen, computed from saved games."""

from __future__ import annotations

import json
from contextlib import closing
from dataclasses import dataclass

from dnb.difficulty.elo import DEFAULT_RATING, update
from dnb.engine import GameState
from dnb.server import db


@dataclass
class PlayerStats:
    games_played: int
    win_rate: float
    boxes_given_away_per_game: float
    rating: float
    level: int


def _count_boxes_given_away(row) -> int:
    """Count human moves that leave a three-sided box for the bot."""

    state = GameState.new(row["rows"], row["cols"])
    human_player = row["human_player"]
    bot_player = 1 - human_player
    count = 0

    moves = json.loads(row["moves"])

    for player, edge in moves:
        if player != state.current_player:
            raise ValueError("Invalid game history: unexpected player turn.")

        state = state.apply(edge)

        # Only count moves after which the bot gets the turn.
        if player == human_player and state.current_player == bot_player:
            if any(state.sides(box) == 3 for box in range(state.layout.num_boxes)):
                count += 1

    return count


def compute_stats(player_id: str) -> PlayerStats:
    """Calculate player statistics from saved SQLite games."""

    with closing(db.connect()) as conn:
        games = conn.execute(
            """
            SELECT player_id, level, rows, cols, human_player,
                   moves, result, finished_at, id
            FROM games
            WHERE player_id = ?
            ORDER BY finished_at ASC, id ASC
            """,
            (player_id,),
        ).fetchall()

    games_played = len(games)

    if games_played == 0:
        return PlayerStats(
            games_played=0,
            win_rate=0.0,
            boxes_given_away_per_game=0.0,
            rating=DEFAULT_RATING,
            level=1,
        )

    wins = 0
    total_boxes_given_away = 0
    rating = DEFAULT_RATING
    latest_level = 1

    for game in games:
        result = game["result"]

        if result == 1.0:
            wins += 1

        total_boxes_given_away += _count_boxes_given_away(game)

        # Update the player's Elo rating chronologically.
        rating, _ = update(rating, DEFAULT_RATING, result)

        if game["level"] is not None:
            latest_level = game["level"]

    return PlayerStats(
        games_played=games_played,
        win_rate=wins / games_played,
        boxes_given_away_per_game=(total_boxes_given_away / games_played),
        rating=rating,
        level=latest_level,
    )
