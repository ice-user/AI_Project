
import pytest

from dnb.difficulty.elo import (
    DEFAULT_RATING,
    expected_score,
    update,
)


def test_default_rating():
    assert DEFAULT_RATING == 1000.0


def test_equal_ratings():
    assert expected_score(1000, 1000) == pytest.approx(0.5)


def test_higher_rated_player_has_higher_expected_score():
    assert expected_score(1200, 1000) > 0.5


def test_lower_rated_player_has_lower_expected_score():
    assert expected_score(1000, 1200) < 0.5


def test_winner_gains_rating():
    new_a, new_b = update(1000, 1000, 1)

    assert new_a > 1000
    assert new_b < 1000


def test_loser_loses_rating():
    new_a, new_b = update(1000, 1000, 0)

    assert new_a < 1000
    assert new_b > 1000


def test_draw():
    new_a, new_b = update(1000, 1000, 0.5)

    assert new_a == pytest.approx(1000)
    assert new_b == pytest.approx(1000)


def test_total_rating_is_preserved():
    new_a, new_b = update(1000, 1200, 1)

    assert new_a + new_b == pytest.approx(2200)


def test_invalid_score():
    with pytest.raises(ValueError):
        update(1000, 1000, 2)


def test_extreme_ratings_do_not_overflow():
    assert expected_score(100000, -100000) == pytest.approx(1)
    assert expected_score(-100000, 100000) == pytest.approx(0)
