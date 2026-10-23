"""FastAPI server (owner: Person 5).

Run:  uv run uvicorn dnb.server.app:app --reload
Docs: http://localhost:8000/docs
"""

from __future__ import annotations

import uuid
from contextlib import closing
from dataclasses import dataclass, field

from fastapi import APIRouter, FastAPI, HTTPException

from dnb.bots import BOTS, Bot, make_bot
from dnb.engine import GameState, IllegalMoveError
from dnb.server import db
from dnb.server.schemas import GameOut, MoveRequest, NewGameRequest, PlayedMove


@dataclass
class Session:
    id: str
    player_id: str
    bot_spec: str
    level: int | None
    bot: Bot
    human_player: int
    state: GameState
    moves: list[tuple[int, int]] = field(default_factory=list)


# Live games live in memory; finished games are saved to SQLite.
GAMES: dict[str, Session] = {}

app = FastAPI(title="Dots and Boxes AI")
api = APIRouter(prefix="/api")


def _out(s: Session) -> GameOut:
    return GameOut(
        id=s.id,
        rows=s.state.rows,
        cols=s.state.cols,
        bot=s.bot_spec,
        human_player=s.human_player,
        current_player=s.state.current_player,
        moves=[PlayedMove(player=p, edge=e) for p, e in s.moves],
        box_owners=list(s.state.owners),
        scores=list(s.state.scores),
        is_over=s.state.is_over(),
        winner=s.state.winner(),
    )


def _play(s: Session, edge: int) -> None:
    s.moves.append((s.state.current_player, edge))
    s.state = s.state.apply(edge)


def _bot_turns(s: Session) -> None:
    """Let the bot move until it's the human's turn again (extra-turn rule) or the game ends."""
    while not s.state.is_over() and s.state.current_player != s.human_player:
        _play(s, s.bot.choose_move(s.state).move)
    if s.state.is_over():
        with closing(db.connect()) as conn:
            db.save_game(
                conn,
                game_id=s.id,
                player_id=s.player_id,
                bot_spec=s.bot_spec,
                level=s.level,
                rows=s.state.rows,
                cols=s.state.cols,
                human_player=s.human_player,
                moves=s.moves,
                scores=s.state.scores,
            )


def _get(game_id: str) -> Session:
    if game_id not in GAMES:
        raise HTTPException(404, "game not found")
    return GAMES[game_id]


@api.get("/bots")
def list_bots() -> list[str]:
    return sorted(BOTS)


@api.post("/games")
def new_game(req: NewGameRequest) -> GameOut:
    try:
        bot = make_bot(req.bot)
    except (ValueError, TypeError) as e:
        raise HTTPException(400, str(e)) from e
    s = Session(
        id=uuid.uuid4().hex,
        player_id=req.player_id,
        bot_spec=req.bot,
        level=req.level,
        bot=bot,
        human_player=0 if req.human_first else 1,
        state=GameState.new(req.rows, req.cols),
    )
    GAMES[s.id] = s
    _bot_turns(s)
    return _out(s)


@api.get("/games/{game_id}")
def get_game(game_id: str) -> GameOut:
    return _out(_get(game_id))


@api.post("/games/{game_id}/move")
def play_move(game_id: str, req: MoveRequest) -> GameOut:
    s = _get(game_id)
    if s.state.is_over() or s.state.current_player != s.human_player:
        raise HTTPException(409, "not your turn")
    try:
        _play(s, req.edge)
    except IllegalMoveError as e:
        raise HTTPException(400, str(e)) from e
    _bot_turns(s)
    return _out(s)


@api.get("/games/{game_id}/hint")
def get_hint(game_id: str):
    # TODO(P4+P5): return dnb.coach.hints.hint() and dangerous_moves() for the current state.
    raise HTTPException(501, "hints not implemented yet (Person 4)")


@api.get("/games/{game_id}/review")
def get_review(game_id: str):
    # TODO(P4+P5): return dnb.coach.review.review_game() + explain_mistakes().
    raise HTTPException(501, "review not implemented yet (Person 4)")


# TODO(P3+P5): GET /api/players/{player_id}/stats -> dnb.difficulty.stats.compute_stats()

app.include_router(api)
