
import pytest

from dnb.difficulty.adjuster import next_level


def test_consistent_wins_increase_level():
    assert next_level(2, [1, 1, 1, 1, 1]) == 3


def test_consistent_losses_decrease_level():
    assert next_level(4, [0, 0, 0, 0, 0]) == 3


def test_balanced_performance_maintains_level():
    assert next_level(3, [1, 0, 1, 0, 0.5]) == 3


def test_too_few_games_maintain_level():
    assert next_level(3, [1, 1]) == 3


def test_level_cannot_exceed_five():
    assert next_level(5, [1, 1, 1, 1, 1]) == 5


def test_level_cannot_go_below_one():
    assert next_level(1, [0, 0, 0, 0, 0]) == 1


def test_only_last_five_results_are_used():
    results = [0, 0, 0, 1, 1, 1, 1, 1]
    assert next_level(3, results) == 4


def test_draws_are_valid_results():
    assert next_level(3, [0.5, 0.5, 0.5]) == 3


def test_invalid_result_is_rejected():
    with pytest.raises(ValueError):
        next_level(3, [1, 1, 2])


def test_invalid_level_is_rejected():
    with pytest.raises(ValueError):
        next_level(6, [1, 1, 1])


def test_exact_win_threshold():
    assert next_level(3, [0.7, 0.7, 0.7]) == 4


def test_exact_loss_threshold():
    assert next_level(3, [0.3, 0.3, 0.3]) == 2
