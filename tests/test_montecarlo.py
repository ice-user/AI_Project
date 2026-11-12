import random

import pytest

from dnb.arena import play_game
from dnb.bots import make_bot
from dnb.bots.greedy import GreedyBot
from dnb.bots.montecarlo import MonteCarloBot
from dnb.engine import GameState


def random_position(rows: int, cols: int, moves: int, seed: int) -> GameState:
    rng = random.Random(seed)
    state = GameState.new(rows, cols)
    for _ in range(moves):
        state = state.apply(rng.choice(state.legal_moves()))
    return state


@pytest.mark.parametrize("greedy", [False, True])
def test_spec_options(greedy):
    bot = make_bot(f"montecarlo:sims=50,greedy_playouts={str(greedy).lower()}")
    assert isinstance(bot, MonteCarloBot)
    assert bot.sims == 50 and bot.greedy_playouts is greedy


@pytest.mark.parametrize("bad", [0, -5, 1.5, True])
def test_rejects_bad_sims(bad):
    with pytest.raises(ValueError):
        MonteCarloBot(sims=bad)


def test_rejects_bad_greedy_flag():
    with pytest.raises(ValueError):
        MonteCarloBot(greedy_playouts="yes")


@pytest.mark.parametrize("greedy", [False, True])
@pytest.mark.parametrize("size", [(1, 1), (2, 3), (3, 3), (5, 5)])
def test_scores_every_legal_move_within_contract(greedy, size):
    state = random_position(*size, moves=3, seed=4)
    scores = MonteCarloBot(sims=60, greedy_playouts=greedy, seed=1).evaluate_moves(state)
    assert set(scores) == set(state.legal_moves())
    assert all(-1.0 <= s <= 1.0 for s in scores.values())


def test_choose_move_is_legal_and_reports_score():
    state = random_position(3, 3, moves=7, seed=2)
    result = MonteCarloBot(sims=100, seed=3).choose_move(state)
    assert result.move in state.legal_moves()
    assert -1.0 <= result.score <= 1.0
    assert result.info["playouts_per_move"] >= 1


def test_finished_game():
    state = random_position(1, 1, moves=4, seed=0)
    bot = MonteCarloBot(sims=10)
    assert bot.evaluate_moves(state) == {}
    with pytest.raises(ValueError):
        bot.choose_move(state)


def test_seed_makes_it_reproducible():
    state = random_position(3, 3, moves=5, seed=9)
    a = MonteCarloBot(sims=200, greedy_playouts=True, seed=7).evaluate_moves(state)
    b = MonteCarloBot(sims=200, greedy_playouts=True, seed=7).evaluate_moves(state)
    assert a == b


def test_last_move_is_scored_exactly():
    """With one edge left there is nothing random: the score is the real result."""
    state = random_position(2, 2, moves=11, seed=5)
    assert len(state.legal_moves()) == 1
    (move,) = state.legal_moves()
    final = state.apply(move)
    me = state.current_player
    margin = final.scores[me] - final.scores[1 - me]
    expected = 1.0 if margin > 0 else 0.0 if margin == 0 else -1.0
    assert MonteCarloBot(sims=5).evaluate_moves(state) == {move: expected}


@pytest.mark.parametrize("greedy", [False, True])
def test_takes_the_free_box(greedy):
    # 1x2 board: box 0 has 3 sides, box 1 has 2. Taking box 0 (edge 4) draws 1-1; any other
    # move hands the opponent both boxes. A decent bot must take it.
    state = GameState.new(1, 2)
    for e in (0, 2, 5, 1):  # top-left, bottom-left, middle vertical, top-right
        state = state.apply(e)
    capture = next(m for m in state.legal_moves() if state.boxes_completed_by(m))
    scores = MonteCarloBot(sims=300, greedy_playouts=greedy, seed=0).evaluate_moves(state)
    assert max(scores, key=scores.__getitem__) == capture


@pytest.mark.parametrize("greedy", [False, True])
def test_playouts_follow_the_engine_rules(greedy):
    """Replay each playout's edges through GameState: same final margin, extra turns included."""
    bot = MonteCarloBot(greedy_playouts=greedy, seed=11)
    playout = bot._greedy_playout if greedy else bot._random_playout
    for seed in range(40):
        state = random_position(3, 4, moves=seed % 20, seed=seed)
        lay = state.layout
        sides = [state.sides(b) for b in range(lay.num_boxes)]
        trace: list[int] = []
        margin = playout(
            lay, state.legal_moves(), sides, state.scores, state.current_player, 0, trace
        )
        assert sorted(trace) == state.legal_moves()
        final = state
        for e in trace:
            final = final.apply(e)
        assert final.scores[0] - final.scores[1] == margin


def test_greedy_playout_moves_match_the_greedy_rule():
    """Every move in a greedy playout is one GreedyBot rates as best."""
    bot = MonteCarloBot(greedy_playouts=True, seed=3)
    for seed in range(20):
        state = random_position(4, 4, moves=seed, seed=seed)
        trace: list[int] = []
        sides = [state.sides(b) for b in range(state.layout.num_boxes)]
        bot._greedy_playout(
            state.layout, state.legal_moves(), sides, state.scores, state.current_player, 0, trace
        )
        for e in trace:
            scores = GreedyBot().evaluate_moves(state)
            # Greedy prefers taking two boxes over one, the playout takes any capture first.
            if scores[e] > 0:
                assert max(scores.values()) > 0
            else:
                assert scores[e] == max(scores.values())
            state = state.apply(e)


def test_greedy_playouts_beat_greedy_bot():
    """Done-when from the brief: the Monte Carlo bot beats the greedy bot."""
    wins = 0
    games = 20
    for i in range(games):
        mc = MonteCarloBot(sims=300, greedy_playouts=True, seed=i)
        greedy = GreedyBot(seed=1000 + i)
        if i % 2 == 0:
            wins += play_game(mc, greedy, 3, 3).winner == 0
        else:
            wins += play_game(greedy, mc, 3, 3).winner == 1
    assert wins >= 14, f"MC won only {wins}/{games}"
