import pytest

from dnb.arena import play_game
from dnb.bots import make_bot, parse_spec
from dnb.bots.random_bot import RandomBot


def test_parse_spec():
    assert parse_spec("minimax:depth=3") == ("minimax", {"depth": 3})
    assert parse_spec("montecarlo:sims=50,greedy_playouts=true") == (
        "montecarlo",
        {"sims": 50, "greedy_playouts": True},
    )
    assert parse_spec("random") == ("random", {})


def test_unknown_bot():
    with pytest.raises(ValueError):
        make_bot("nope")


@pytest.mark.parametrize("size", [(1, 1), (2, 3), (3, 3), (5, 5)])
def test_checkpoint_two_random_bots_play_a_full_game(size):
    """Phase 1 checkpoint from the brief. Must stay green forever."""
    rows, cols = size
    rec = play_game(RandomBot(seed=1), RandomBot(seed=2), rows, cols)
    assert sum(rec.scores) == rows * cols
    assert len(rec.moves) == (rows + 1) * cols + rows * (cols + 1)
