import pytest


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Never let tests write to the real data/games.sqlite."""
    from dnb.server import db

    monkeypatch.setattr(db, "DB_PATH", tmp_path / "games.sqlite")
