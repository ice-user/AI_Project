"""Bots (owners: Person 1 and Person 2). All share the Bot interface in base.py."""

from dnb.bots.base import Bot, MoveResult
from dnb.bots.registry import BOTS, make_bot, parse_spec

__all__ = ["BOTS", "Bot", "MoveResult", "make_bot", "parse_spec"]
