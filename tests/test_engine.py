import pytest

from dnb.engine import GameState, IllegalMoveError, edge_coords, h_edge, layout, v_edge


def test_edge_counts():
    lay = layout(3, 3)
    assert lay.num_edges == 24
    assert lay.num_boxes == 9
    assert len(GameState.new(3, 3).legal_moves()) == 24


def test_edge_coords_round_trip():
    rows, cols = 2, 3
    for e in range(layout(rows, cols).num_edges):
        kind, r, c = edge_coords(rows, cols, e)
        assert (h_edge if kind == "h" else v_edge)(rows, cols, r, c) == e


def test_turn_passes_when_no_box_completed():
    s = GameState.new(2, 2).apply(0)
    assert s.current_player == 1


def test_completing_a_box_gives_an_extra_turn():
    # 2x2 board, box 0 has edges top=0, bottom=2, left=6, right=7
    s = GameState.new(2, 2)
    for e in (0, 2, 6):  # players alternate: 0, 1, 0
        s = s.apply(e)
    assert s.current_player == 1
    s = s.apply(7)
    assert s.scores == (0, 1)
    assert s.owners[0] == 1
    assert s.current_player == 1  # same player moves again


def test_one_edge_can_complete_two_boxes():
    # The example from the brief: 1x2 board, middle edge (5) finishes both boxes.
    s = GameState.new(1, 2)
    for e in (0, 1, 2, 3, 4, 6):
        s = s.apply(e)
    mover = s.current_player
    s = s.apply(5)
    assert s.scores[mover] == 2
    assert s.is_over()
    assert s.winner() == mover


def test_illegal_moves():
    s = GameState.new(2, 2).apply(0)
    with pytest.raises(IllegalMoveError):
        s.apply(0)
    with pytest.raises(IllegalMoveError):
        s.apply(99)


def test_state_is_immutable():
    s = GameState.new(2, 2)
    s.apply(0)
    assert s.drawn == 0
