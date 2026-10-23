# Shared test positions

Known board positions that more than one person tests against, so everyone agrees on the rules
and on what a "good" move is. Add one whenever you find a tricky case.

Format: one JSON file per position.

```json
{
  "rows": 2,
  "cols": 2,
  "drawn": [0, 2, 6],
  "current_player": 0,
  "note": "Taking box 0 is free; edge 7 completes it.",
  "best_moves": [7],
  "bad_moves": []
}
```

Load with `GameState.new(rows, cols)` then `apply()` each drawn edge, or build the state directly.
