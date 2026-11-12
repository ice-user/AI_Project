import pytest

from dnb.bots.registry import make_bot
from dnb.difficulty.levels import LEVELS, bot_spec_for_level


def test_five_difficulty_levels_exist():
    assert len(LEVELS) == 5


@pytest.mark.parametrize("level", [1, 2, 3, 4, 5])
def test_every_level_has_a_name_and_bot(level):
    assert "name" in LEVELS[level]
    assert "bot" in LEVELS[level]


@pytest.mark.parametrize("level", [1, 2, 3, 4, 5])
def test_bot_specification_is_valid(level):
    spec = bot_spec_for_level(level)
    bot = make_bot(spec)

    assert bot is not None


def test_beginner_uses_greedy():
    assert bot_spec_for_level(1) == "greedy:randomness=0.5"


def test_medium_uses_minimax():
    assert bot_spec_for_level(3) == "minimax:depth=2"


def test_hard_uses_deeper_minimax():
    assert bot_spec_for_level(4) == "minimax:depth=4"


def test_expert_uses_monte_carlo():
    assert bot_spec_for_level(5) == (
        "montecarlo:sims=2000,greedy_playouts=true"
    )


@pytest.mark.parametrize("level", [0, 6, -1])
def test_invalid_levels_are_rejected(level):
    with pytest.raises(ValueError):
        bot_spec_for_level(level)


def test_non_integer_level_is_rejected():
    with pytest.raises(ValueError):
        bot_spec_for_level("3")
