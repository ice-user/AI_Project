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


def test_unknown_bot_is_rejected():
    assert client.post("/api/games", json={"bot": "nope"}).status_code == 400
