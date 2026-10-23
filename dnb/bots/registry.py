"""Build bots from short text specs, e.g. "random", "minimax:depth=3", "montecarlo:sims=2000".

The server, difficulty levels and arena all create bots through `make_bot`, so a new bot
only has to be added to BOTS below to be usable everywhere.
"""

from __future__ import annotations

from dnb.bots.base import Bot
from dnb.bots.greedy import GreedyBot
from dnb.bots.minimax import MinimaxBot
from dnb.bots.montecarlo import MonteCarloBot
from dnb.bots.random_bot import RandomBot

BOTS: dict[str, type[Bot]] = {
    "random": RandomBot,
    "greedy": GreedyBot,
    "minimax": MinimaxBot,
    "montecarlo": MonteCarloBot,
}


def _parse_value(raw: str) -> int | float | bool | str:
    if raw.lower() in ("true", "false"):
        return raw.lower() == "true"
    for cast in (int, float):
        try:
            return cast(raw)
        except ValueError:
            pass
    return raw


def parse_spec(spec: str) -> tuple[str, dict[str, int | float | bool | str]]:
    """'minimax:depth=3,foo=1' -> ('minimax', {'depth': 3, 'foo': 1})"""
    name, _, args = spec.partition(":")
    kwargs = {}
    for part in filter(None, args.split(",")):
        key, _, value = part.partition("=")
        kwargs[key.strip()] = _parse_value(value.strip())
    return name.strip(), kwargs


def make_bot(spec: str) -> Bot:
    name, kwargs = parse_spec(spec)
    if name not in BOTS:
        raise ValueError(f"unknown bot {name!r}; known: {sorted(BOTS)}")
    return BOTS[name](**kwargs)
