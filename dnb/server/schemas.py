"""API request/response shapes. CONTRACT: web/src/api.ts mirrors these; change both together."""

from __future__ import annotations

from pydantic import BaseModel, Field


class NewGameRequest(BaseModel):
    rows: int = Field(3, ge=1, le=7)
    cols: int = Field(3, ge=1, le=7)
    bot: str = "random"  # bot spec, see dnb/bots/registry.py
    level: int | None = None  # TODO(P3/P5): when set, pick the bot from dnb.difficulty.levels
    human_first: bool = True
    player_id: str = "guest"


class MoveRequest(BaseModel):
    edge: int


class PlayedMove(BaseModel):
    player: int
    edge: int


class GameOut(BaseModel):
    id: str
    rows: int
    cols: int
    bot: str
    human_player: int
    current_player: int
    moves: list[PlayedMove]
    box_owners: list[int]  # -1 = unclaimed
    scores: list[int]
    is_over: bool
    winner: int | None
