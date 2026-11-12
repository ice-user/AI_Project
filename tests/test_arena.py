import csv

import pytest

from dnb.arena.run_arena import build_bot, format_table, main, read_csv, run_arena, write_csv

SPECS = ["random", "greedy", "montecarlo:sims=40,greedy_playouts=true"]


@pytest.fixture(scope="module")
def result():
    return run_arena(SPECS, games_per_pair=6, rows=2, cols=2, seed=1)


def test_every_pair_plays_every_game(result):
    assert [(p.a, p.b) for p in result.pairs] == [
        (SPECS[0], SPECS[1]),
        (SPECS[0], SPECS[2]),
        (SPECS[1], SPECS[2]),
    ]
    for p in result.pairs:
        assert p.games == 6
        assert p.wins_a + p.wins_b + p.draws == 6
        assert p.boxes_a + p.boxes_b == 6 * 4
        assert p.moves_a + p.moves_b == 6 * 12
        assert p.moves_a > 0 and p.moves_b > 0


def test_scores_are_symmetric(result):
    for p in result.pairs:
        assert result.score(p.a, p.b) + result.score(p.b, p.a) == pytest.approx(1.0)


def test_summaries_add_up(result):
    summaries = {s.spec: s for s in result.summaries()}
    assert all(s.games == 12 for s in summaries.values())
    assert sum(s.wins for s in summaries.values()) == sum(s.losses for s in summaries.values())


def test_same_seed_same_results():
    a = run_arena(["random", "greedy"], games_per_pair=8, rows=2, cols=2, seed=5)
    b = run_arena(["random", "greedy"], games_per_pair=8, rows=2, cols=2, seed=5)
    key = lambda r: [(p.wins_a, p.wins_b, p.draws, p.boxes_a) for p in r.pairs]  # noqa: E731
    assert key(a) == key(b)


def test_parallel_matches_serial():
    serial = run_arena(["random", "greedy"], games_per_pair=8, rows=2, cols=2, seed=3)
    parallel = run_arena(["random", "greedy"], 8, 2, 2, seed=3, workers=2)
    assert serial.pairs[0].wins_a == parallel.pairs[0].wins_a
    assert serial.pairs[0].boxes_a == parallel.pairs[0].boxes_a


def test_swaps_who_starts():
    # On a 1x1 board the 4th (last) edge is always drawn by the second player, who wins.
    # So with alternating starts each bot wins exactly half the games.
    r = run_arena(["random", "greedy"], games_per_pair=10, rows=1, cols=1, seed=0)
    assert (r.pairs[0].wins_a, r.pairs[0].wins_b) == (5, 5)


def test_build_bot_adds_seed_only_when_supported():
    assert build_bot("random", 4).rng.random() == build_bot("random", 4).rng.random()
    assert build_bot("random:seed=1", 4).rng.random() == build_bot("random:seed=1", 9).rng.random()
    assert build_bot("minimax:depth=2", 4).depth == 2  # minimax takes no seed


def test_typo_fails_before_playing():
    with pytest.raises(ValueError):
        run_arena(["random", "nope"], games_per_pair=1)


def test_csv_and_table(result, tmp_path):
    pairs_path, bots_path = write_csv(result, tmp_path)
    with pairs_path.open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3 and rows[0]["bot_a"] == "random" and rows[0]["games"] == "6"
    with bots_path.open() as f:
        assert [r["bot"] for r in csv.DictReader(f)] == SPECS
    loaded = read_csv(pairs_path)
    assert loaded.specs == result.specs and (loaded.rows, loaded.cols) == (2, 2)
    for got, want in zip(loaded.pairs, result.pairs, strict=True):
        assert (got.wins_a, got.draws, got.boxes_a, got.moves_b) == (
            want.wins_a,
            want.draws,
            want.boxes_a,
            want.moves_b,
        )
        assert got.ms_per_move_a == pytest.approx(want.ms_per_move_a, abs=1e-3)
    table = format_table(result)
    assert all(spec in table for spec in SPECS)


def test_cli_with_charts(tmp_path, capsys):
    pytest.importorskip("matplotlib")
    main(
        ["--specs", "random", "greedy", "--games", "4", "--rows", "2", "--cols", "2"]
        + ["--workers", "1", "--out", str(tmp_path), "--charts"]
    )
    names = {p.name for p in tmp_path.iterdir()}
    assert {"arena_2x2_pairs.csv", "arena_2x2_bots.csv"} <= names
    assert {"arena_2x2_matrix.png", "arena_2x2_strength.png"} <= names
    assert "Win rate" in capsys.readouterr().out


def test_sweep(tmp_path):
    pytest.importorskip("matplotlib")
    from dnb.arena.sweep import main as sweep_main

    sweep_main(
        ["--sims", "10", "40", "--games", "4", "--rows", "2", "--cols", "2"]
        + ["--workers", "1", "--out", str(tmp_path)]
    )
    assert (tmp_path / "sweep_2x2.csv").exists() and (tmp_path / "sweep_2x2.png").exists()
