from fastapi.testclient import TestClient

from dnb.server.app import app

client = TestClient(app)


def test_play_a_full_game_against_random_bot():
    game = client.post("/api/games", json={"rows": 2, "cols": 2, "bot": "random:seed=0"}).json()
    while not game["is_over"]:
        drawn = {m["edge"] for m in game["moves"]}
        edge = next(e for e in range(12) if e not in drawn)
        resp = client.post(f"/api/games/{game['id']}/move", json={"edge": edge})
        assert resp.status_code == 200, resp.text
        game = resp.json()
    assert sum(game["scores"]) == 4


def test_illegal_move_is_rejected():
    game = client.post("/api/games", json={"rows": 2, "cols": 2}).json()
    assert client.post(f"/api/games/{game['id']}/move", json={"edge": 999}).status_code == 400


def test_rejected_moves_are_not_recorded(monkeypatch):
    """A rejected move must leave the game untouched. If it stayed in the move list, the saved
    game could not be replayed, so its review and the player's stats would fail for good."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)  # the review must not call a real LLM
    body = {"rows": 2, "cols": 2, "bot": "random:seed=0", "player_id": "dave"}
    game = client.post("/api/games", json=body).json()
    url = f"/api/games/{game['id']}"

    assert client.post(f"{url}/move", json={"edge": 999}).status_code == 400
    assert client.get(url).json()["moves"] == game["moves"]

    game = client.post(f"{url}/move", json={"edge": 0}).json()
    if not game["is_over"]:
        assert client.post(f"{url}/move", json={"edge": 0}).status_code == 400  # already drawn
        assert client.get(url).json()["moves"] == game["moves"]

    while not game["is_over"]:
        drawn = {m["edge"] for m in game["moves"]}
        edge = next(e for e in range(12) if e not in drawn)
        game = client.post(f"{url}/move", json={"edge": edge}).json()
    assert client.get(f"{url}/review").status_code == 200
    assert client.get("/api/players/dave/stats").json()["games_played"] == 1


def test_unknown_bot_is_rejected():
    assert client.post("/api/games", json={"bot": "nope"}).status_code == 400
