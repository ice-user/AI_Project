import json

from dnb.difficulty.stats import compute_stats
from dnb.server import db


def insert_game(
    player_id,
    game_id,
    result,
    level=2,
    moves=None,
    score_human=0,
    score_bot=0,
):
    with db.connect() as conn:
        conn.execute(
            """
            INSERT INTO games (
                id, player_id, bot_spec, level, rows, cols,
                human_player, moves, score_human, score_bot, result
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                game_id,
                player_id,
                "greedy",
                level,
                1,
                1,
                0,
                json.dumps(moves or []),
                score_human,
                score_bot,
                result,
            ),
        )


def test_new_player_has_default_stats():
    stats = compute_stats("new_player")

    assert stats.games_played == 0
    assert stats.win_rate == 0.0
    assert stats.boxes_given_away_per_game == 0.0
    assert stats.rating == 1000.0
    assert stats.level == 1


def test_games_played_and_win_rate():
    insert_game("player1", "game1", 1.0)
    insert_game("player1", "game2", 0.0)

    stats = compute_stats("player1")

    assert stats.games_played == 2
    assert stats.win_rate == 0.5


def test_latest_recorded_level():
    insert_game("player1", "game1", 1.0, level=2)
    insert_game("player1", "game2", 0.0, level=4)

    stats = compute_stats("player1")

    assert stats.level == 4


def test_boxes_given_away():
    # Human draws edges 0 and 2.
    # Bot draws edges 1 and 3.
    # After the human's second move, the bot receives a
    # three-sided box and completes it.

    moves = [
        [0, 0],
        [1, 1],
        [0, 2],
        [1, 3],
    ]

    insert_game(
        "player1",
        "game1",
        result=0.0,
        level=2,
        moves=moves,
        score_human=0,
        score_bot=1,
    )

    stats = compute_stats("player1")

    assert stats.boxes_given_away_per_game == 1.0


def test_rating_changes_after_game():
    insert_game("player1", "game1", 1.0)

    stats = compute_stats("player1")

    assert stats.rating > 1000.0


def test_other_players_games_are_not_counted():
    insert_game("player1", "game1", 1.0)
    insert_game("player2", "game2", 1.0)

    stats = compute_stats("player1")

    assert stats.games_played == 1
