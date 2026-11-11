# Sample coach UI (do not merge)

This branch is a working sample of the hint, danger and review features in the web app, for
whoever builds the real frontend (Person 5). Take what is useful; it is not meant to be merged
as it is.

## What it shows

- **Hint** button: calls `GET /api/games/{id}/hint` and draws the suggested line as a dotted
  green line.
- **Show danger** checkbox: calls `GET /api/games/{id}/danger` after every move and shades lines
  that would leave a box with 3 sides.
- **Review** list after the game: calls `GET /api/games/{id}/review` and shows each of the
  player's moves as Good / Okay / Mistake, with explanations for the biggest mistakes.
- Clicking a reviewed move rewinds the board to just before it, colours the played line by its
  label and draws the better move dashed.

## Where the code is

| File | Change |
|---|---|
| `web/src/App.tsx` | Hint button, danger toggle, review list, rewinding to a reviewed move |
| `web/src/Board.tsx` | Optional `marks` prop: edge -> highlight kind, drawn over the board |
| `web/src/geometry.ts` | `boxEdges()`, used to rebuild box owners when rewinding |
| `web/src/styles.css` | Highlight colours, label badges, review list |

The API calls and types it uses are already on `main` in `web/src/api.ts`.

## Run it

```bash
git switch p4/sample-coach-ui
uv run python scripts/dev.py
```

Then open http://localhost:5173, pick `minimax`, play a game, and use Hint and Show danger.
The review appears when the game ends.
