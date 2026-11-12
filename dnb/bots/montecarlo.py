"""Monte Carlo bot (owner: Person 2).

For each legal move, play quick games ("playouts") to the end and pick the move that wins most.
There is no lookahead tree: all the knowledge comes from the playouts.

Options (all usable from a registry spec, e.g. "montecarlo:sims=2000,greedy_playouts=true"):

* ``sims``: total playouts per decision, shared evenly between the legal moves (every move
  gets at least one). More playouts = stronger and slower. This is the strength setting that
  difficulty levels use.
* ``greedy_playouts``: when true, the simulated players follow the greedy rule (take a box if
  you can, otherwise avoid giving one away) instead of moving at random. Same cost per playout,
  much more realistic games, so a much stronger bot for the same ``sims``.
* ``seed``: makes the bot reproducible (tests, arena).

Score of a move = ``2 * win_rate - 1`` from the point of view of the player to move, where a
draw counts as half a win. That is the [-1, 1] scale the Bot contract asks for.

Speed: playouts do not build a ``GameState`` per move. They run on a plain bitmask plus a
per-box side counter, using the engine's precomputed ``Layout``. ``tests/test_montecarlo.py``
replays playouts through the real engine to make sure both agree on the rules.

Stretch goal: full MCTS (UCT) in a separate class, same interface.
"""

from __future__ import annotations

import random

from dnb.bots.base import Bot, MoveResult
from dnb.engine import GameState
from dnb.engine.state import Layout

# How many random picks a greedy playout tries before scanning all edges for a safe one.
_SAFE_SAMPLE_TRIES = 6


class MonteCarloBot(Bot):
    name = "montecarlo"

    def __init__(self, sims: int = 200, greedy_playouts: bool = False, seed: int | None = None):
        if isinstance(sims, bool) or not isinstance(sims, int) or sims < 1:
            raise ValueError("sims must be a positive integer")
        if not isinstance(greedy_playouts, bool):
            raise ValueError("greedy_playouts must be true or false")
        self.sims = sims  # total simulations per move decision; more = stronger
        self.greedy_playouts = greedy_playouts  # follow the greedy rule in playouts
        self.rng = random.Random(seed)

    # ------------------------------------------------------------------ Bot interface

    def evaluate_moves(self, state: GameState) -> dict[int, float]:
        """Score every legal move as 2 * win_rate - 1 for the player to move."""
        return {move: 2 * rate - 1 for move, rate in self._win_rates(state).items()}

    def choose_move(self, state: GameState) -> MoveResult:
        rates = self._win_rates(state)
        if not rates:
            raise ValueError("cannot choose a move in a finished game")
        best = max(rates.values())
        move = self.rng.choice([m for m, r in rates.items() if r == best])
        return MoveResult(
            move=move,
            score=2 * best - 1,
            info={"playouts_per_move": self._per_move(len(rates)), "win_rate": best},
        )

    # ------------------------------------------------------------------ internals

    def _per_move(self, num_moves: int) -> int:
        return max(1, self.sims // num_moves)

    def _win_rates(self, state: GameState) -> dict[int, float]:
        moves = state.legal_moves()
        if not moves:
            return {}
        lay = state.layout
        me = state.current_player
        per_move = self._per_move(len(moves))
        base_sides = [state.sides(b) for b in range(lay.num_boxes)]
        playout = self._greedy_playout if self.greedy_playouts else self._random_playout

        rates = {}
        for move in moves:
            # Apply the candidate move once, then run every playout from the result.
            child = state.apply(move)
            sides = base_sides[:]
            for b in lay.edge_boxes[move]:
                sides[b] += 1
            remaining = [e for e in moves if e != move]
            wins = 0.0
            for _ in range(per_move):
                margin = playout(lay, remaining, sides, child.scores, child.current_player, me)
                wins += 1.0 if margin > 0 else 0.5 if margin == 0 else 0.0
            rates[move] = wins / per_move
        return rates

    def _random_playout(
        self,
        lay: Layout,
        remaining: list[int],
        sides: list[int],
        scores: tuple[int, int],
        player: int,
        me: int,
        trace: list[int] | None = None,
    ) -> int:
        """Both players move uniformly at random. Returns my final box margin.

        With random moves the order of edges is just a random permutation, so we shuffle
        once and walk it, tracking whose turn it is (the extra-turn rule).
        `trace`, if given, receives every edge drawn (tests replay it through the engine).
        """
        order = remaining[:]
        self.rng.shuffle(order)
        if trace is not None:
            trace.extend(order)
        sides = sides[:]
        score = list(scores)
        edge_boxes = lay.edge_boxes
        for e in order:
            completed = 0
            for b in edge_boxes[e]:
                sides[b] += 1
                if sides[b] == 4:
                    completed += 1
            if completed:
                score[player] += completed
            else:
                player = 1 - player
        return score[me] - score[1 - me]

    def _greedy_playout(
        self,
        lay: Layout,
        remaining: list[int],
        sides: list[int],
        scores: tuple[int, int],
        player: int,
        me: int,
        trace: list[int] | None = None,
    ) -> int:
        """Both players follow the greedy rule. Returns my final box margin.

        Each turn, in order of preference:
          1. complete a box (an edge of a box that already has 3 sides);
          2. play a safe edge (it leaves no box with 3 sides), picked at random;
          3. give away as few boxes as possible (an edge touching one 2-sided box, not two).
        Once safe edges run out they never come back (sides only grow), so we stop looking.
        `trace`, if given, receives every edge drawn (tests replay it through the engine).
        """
        rng = self.rng
        edge_boxes = lay.edge_boxes
        box_edges = lay.box_edges
        sides = sides[:]
        score = list(scores)
        left = remaining[:]  # undrawn edges, order does not matter
        pos = {e: i for i, e in enumerate(left)}  # undrawn edge -> index in `left`
        three = [b for b, s in enumerate(sides) if s == 3]  # may hold stale entries
        safe_left = True

        def draw(e: int) -> int:
            # swap-remove e from `left`
            i = pos.pop(e)
            last = left.pop()
            if last != e:
                left[i] = last
                pos[last] = i
            completed = 0
            for b in edge_boxes[e]:
                sides[b] += 1
                if sides[b] == 4:
                    completed += 1
                elif sides[b] == 3:
                    three.append(b)
            return completed

        def is_safe(e: int) -> bool:
            return all(sides[b] < 2 for b in edge_boxes[e])

        while left:
            move = -1
            # 1. capture
            while three:
                b = three.pop()
                if sides[b] == 3:
                    move = next(e for e in box_edges[b] if e in pos)
                    break
            # 2. safe edge
            if move < 0 and safe_left:
                for _ in range(_SAFE_SAMPLE_TRIES):
                    e = left[rng.randrange(len(left))]
                    if is_safe(e):
                        move = e
                        break
                else:
                    candidates = [e for e in left if is_safe(e)]
                    if candidates:
                        move = rng.choice(candidates)
                    else:
                        safe_left = False
            # 3. smallest sacrifice
            if move < 0:
                one = [e for e in left if sum(sides[b] == 2 for b in edge_boxes[e]) <= 1]
                move = rng.choice(one or left)

            if trace is not None:
                trace.append(move)
            completed = draw(move)
            if completed:
                score[player] += completed
            else:
                player = 1 - player
        return score[me] - score[1 - me]
