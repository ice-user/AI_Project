"""Dots and Boxes game state and rules.

CONTRACT (see docs/ARCHITECTURE.md): the public API of this module is frozen.
Changing a signature needs a PR approved by the whole team.

Board model
-----------
A board has `rows x cols` boxes, so `(rows+1) x (cols+1)` dots.
Every edge (line between two neighbouring dots) has an integer index:

* horizontal edges first:  h(r, c) = r * cols + c                 r in [0, rows], c in [0, cols)
* then vertical edges:     v(r, c) = H + r * (cols + 1) + c       r in [0, rows), c in [0, cols]
  where H = (rows + 1) * cols is the number of horizontal edges.

Box (r, c) has index r * cols + c and is bordered by
top h(r, c), bottom h(r+1, c), left v(r, c), right v(r, c+1).

A move is just an edge index. Players are 0 and 1.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache


class IllegalMoveError(ValueError):
    """Raised when a move is out of range or the edge is already drawn."""


@dataclass(frozen=True)
class Layout:
    """Precomputed geometry for one board size. Shared by every state of that size."""

    rows: int
    cols: int
    num_h: int
    num_edges: int
    num_boxes: int
    edge_boxes: tuple[tuple[int, ...], ...]  # edge -> boxes it borders (1 or 2)
    box_edges: tuple[tuple[int, int, int, int], ...]  # box -> (top, bottom, left, right)


@cache
def layout(rows: int, cols: int) -> Layout:
    if rows < 1 or cols < 1:
        raise ValueError("board needs at least 1x1 boxes")
    num_h = (rows + 1) * cols
    num_edges = num_h + rows * (cols + 1)
    box_edges = []
    edge_boxes: list[list[int]] = [[] for _ in range(num_edges)]
    for r in range(rows):
        for c in range(cols):
            b = r * cols + c
            edges = (
                h_edge(rows, cols, r, c),
                h_edge(rows, cols, r + 1, c),
                v_edge(rows, cols, r, c),
                v_edge(rows, cols, r, c + 1),
            )
            box_edges.append(edges)
            for e in edges:
                edge_boxes[e].append(b)
    return Layout(
        rows=rows,
        cols=cols,
        num_h=num_h,
        num_edges=num_edges,
        num_boxes=rows * cols,
        edge_boxes=tuple(tuple(bs) for bs in edge_boxes),
        box_edges=tuple(box_edges),
    )


def h_edge(rows: int, cols: int, r: int, c: int) -> int:
    return r * cols + c


def v_edge(rows: int, cols: int, r: int, c: int) -> int:
    return (rows + 1) * cols + r * (cols + 1) + c


def edge_coords(rows: int, cols: int, edge: int) -> tuple[str, int, int]:
    """Edge index -> ("h" | "v", r, c). Handy for the UI and for debugging."""
    num_h = (rows + 1) * cols
    if edge < num_h:
        return ("h", edge // cols, edge % cols)
    k = edge - num_h
    return ("v", k // (cols + 1), k % (cols + 1))


@dataclass(frozen=True, slots=True)
class GameState:
    """Immutable game state. `apply()` returns a new state; nothing is mutated."""

    rows: int
    cols: int
    drawn: int = 0  # bitmask: bit e is set when edge e is drawn
    owners: tuple[int, ...] = ()  # per box: -1 unclaimed, else the player who claimed it
    scores: tuple[int, int] = (0, 0)
    current_player: int = 0

    @classmethod
    def new(cls, rows: int = 3, cols: int = 3) -> GameState:
        lay = layout(rows, cols)
        return cls(rows=rows, cols=cols, owners=(-1,) * lay.num_boxes)

    @property
    def layout(self) -> Layout:
        return layout(self.rows, self.cols)

    def is_drawn(self, edge: int) -> bool:
        return bool(self.drawn >> edge & 1)

    def legal_moves(self) -> list[int]:
        return [e for e in range(self.layout.num_edges) if not self.drawn >> e & 1]

    def is_over(self) -> bool:
        return self.drawn == (1 << self.layout.num_edges) - 1

    def winner(self) -> int | None:
        """Winning player, or None if the game is unfinished or a draw."""
        if not self.is_over() or self.scores[0] == self.scores[1]:
            return None
        return 0 if self.scores[0] > self.scores[1] else 1

    def sides(self, box: int) -> int:
        """Number of drawn sides of a box (0-4)."""
        return sum(self.drawn >> e & 1 for e in self.layout.box_edges[box])

    def boxes_completed_by(self, move: int) -> int:
        """How many boxes `move` would complete (0, 1 or 2). Does not check legality."""
        lay = self.layout
        return sum(1 for b in lay.edge_boxes[move] if self.sides(b) == 3)

    def apply(self, move: int) -> GameState:
        """Draw `move`. Completing a box scores it and the same player moves again."""
        lay = self.layout
        if not 0 <= move < lay.num_edges or self.drawn >> move & 1:
            raise IllegalMoveError(f"illegal move {move}")
        drawn = self.drawn | (1 << move)
        owners = list(self.owners)
        completed = 0
        for b in lay.edge_boxes[move]:
            if all(drawn >> e & 1 for e in lay.box_edges[b]):
                owners[b] = self.current_player
                completed += 1
        scores = list(self.scores)
        scores[self.current_player] += completed
        return GameState(
            rows=self.rows,
            cols=self.cols,
            drawn=drawn,
            owners=tuple(owners),
            scores=(scores[0], scores[1]),
            current_player=self.current_player if completed else 1 - self.current_player,
        )

    def drawn_edges(self) -> list[int]:
        return [e for e in range(self.layout.num_edges) if self.drawn >> e & 1]
