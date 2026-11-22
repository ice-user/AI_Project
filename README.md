# Dots and Boxes AI

A web game where you play Dots and Boxes against AI opponents of increasing strength. The game
warns you about risky moves, gives hints, reviews your game move by move, and explains your
biggest mistakes in plain language. The same AI agents are also compared offline in a bot
arena.

Semester project at Shiv Nadar University by a team of five. Original brief:
[docs/project-brief.pdf](docs/project-brief.pdf).

## Team

| # | Member | Area | What they handled | Folder |
|---|---|---|---|---|
| 1 | **Yashvardhan Singh Chauhan** | Game engine and classic bots | Set up the project scaffold (repository, CI, first server and web app). Built the rules engine (immutable game state, legal moves, scoring, extra-turn rule) and the random, greedy and alpha-beta minimax bots, with contract tests and timing benchmarks. Added the custom-bot picker. | `dnb/engine/`, `dnb/bots/` |
| 2 | **Suhani Rohilla** | Monte Carlo bot and arena | Built the Monte Carlo bot with random and greedy rollouts. Built the bot-vs-bot arena, the simulation-budget sweep and the result charts. | `dnb/bots/montecarlo.py`, `dnb/arena/` |
| 3 | **Raeena Kausar** | Adaptive difficulty | Defined the five difficulty levels, the Elo rating, the auto-adjust rule and player statistics. | `dnb/difficulty/` |
| 4 | **Abhiraj Agarwal** | Hints and review | Built the danger highlight, the hint button, the post-game move review (Good / Okay / Mistake) and fact-checked LLM explanations of mistakes, plus their API endpoints. | `dnb/coach/` |
| 5 | **Sannidhya Rai** | Web app and integration | Built the Play, Review and Profile screens (difficulty picker, board, hints, danger overlay). Added level-based games, game history and the stats endpoint to the FastAPI server, and the one-command demo mode. | `web/`, `dnb/server/`, `scripts/` |

## Features

- **Play** on a 2×2 to 5×5 board against five difficulty levels, from Beginner to Expert, or
  against any bot with custom settings (for example `minimax:depth=3`). You choose who moves
  first.
- **Danger highlight:** lines that would hand the bot a free box are marked on each of your
  turns.
- **Hints:** the best move according to a minimax search, kept to about a second per hint.
- **Review:** after the game, every one of your moves is labelled Good, Okay or Mistake against
  the best move found.
- **Explanations:** for the biggest mistakes, Gemini writes a one or two sentence explanation
  using only facts from the review. If the call fails, or the answer contradicts those facts,
  a template sentence is shown instead.
- **Profile:** rating, games played, win rate, boxes given away per game and recent games. Any past game can be
  opened for review, even after a server restart.

### Difficulty levels

| Level | Name | Bot |
|---|---|---|
| 1 | Beginner | Greedy, plays a random move half the time |
| 2 | Easy | Greedy (takes boxes, avoids giving them away) |
| 3 | Medium | Minimax, depth 2 |
| 4 | Hard | Minimax, depth 4 |
| 5 | Expert | Monte Carlo, 2000 simulations, greedy rollouts |

## Key results

Measured on a 3×3 board, 100 games per pairing (details in [docs/report/](docs/report/)):

- Monte Carlo with greedy rollouts (500 simulations) wins **96%** of games against greedy and
  **85%** against depth-4 minimax, at about **17 ms per move**, less than half the time of
  depth-4 minimax.
- The same Monte Carlo bot with **random** rollouts loses **every** game against greedy. The
  rollout policy matters far more than the number of simulations.
- Raising the simulation budget from 500 to 2000 adds almost no strength (51–49 head to head)
  and costs about 4× the time.

## Quick start

You need [uv](https://docs.astral.sh/uv/) and Node.js 20+.

```bash
uv sync --all-extras          # Python 3.12 + all dependencies, identical for everyone
cd web && npm install && cd ..
uv run python scripts/dev.py  # starts the API (:8000) and the web app (:5173)
```

Open http://localhost:5173. API docs: http://localhost:8000/docs.

**AI explanations (optional):** copy `.env.example` to `.env` and set `GEMINI_API_KEY`
([get a free key](https://aistudio.google.com/apikey)). Without a key, the app shows template
explanations. Never commit `.env`.

**For a presentation:** `uv run python scripts/dev.py --demo` builds the web app once and serves
everything from http://localhost:8000, with no auto-reload. Add `--port 8001` to use another
port.

### Troubleshooting

- **`[WinError 10013]` or "address already in use" on startup:** another program is using port
  8000. Find it with `Get-NetTCPConnection -LocalPort 8000` (PowerShell) or `lsof -i :8000`
  (macOS/Linux) and stop it. Or run `scripts/dev.py --demo --port 8001`. Development mode
  needs port 8000, because the web app's dev proxy points there.
- **"Can't reach the server" in the browser:** the API is not running. Check the terminal
  running `dev.py` for an error.
- **Explanations always read like a template:** the key is missing from `.env`, or Gemini is
  temporarily unavailable. The server log says which.

## Everyday commands

```bash
uv run pytest                                  # all tests
uv run ruff check . --fix                      # lint
uv run ruff format .                           # format
uv run python -m dnb.arena.run_arena --charts  # bot-vs-bot tournament + charts
uv run python -m dnb.arena.sweep               # Monte Carlo simulation-budget sweep
```

## Project structure

```
dnb/
  engine/       rules engine: immutable GameState, moves as edge indices, extra-turn rule
  bots/         Bot interface, registry ("minimax:depth=4"), random/greedy/minimax/montecarlo
  arena/        bot-vs-bot tournament, simulation sweep, charts
  difficulty/   levels, Elo rating, auto-adjust rule, player statistics
  coach/        danger highlight, hints, move review, LLM explanations
  server/       FastAPI app, request/response schemas, SQLite game history
web/            React + TypeScript + Vite client (Play, Review, Profile)
scripts/        dev.py (one-command start), benchmarks
tests/          pytest suite and shared board-position fixtures
docs/           architecture, roadmap, per-person results
```

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): how the parts fit together, and the frozen
  contracts (engine, bot interface, registry, API and database).
- [CONTRIBUTING.md](CONTRIBUTING.md): branches, pull requests and reviews.
- [docs/ROADMAP.md](docs/ROADMAP.md): the plan and each person's task list.
- [docs/PERSON1_HANDOFF.md](docs/PERSON1_HANDOFF.md): engine and classic bots, usage and
  measurements.
- Results by area: [Person 1](docs/report/PERSON1_RESULTS.md),
  [Person 2](docs/report/PERSON2_RESULTS.md), [Person 3](docs/report/PERSON3_RESULTS.md).

## Known limitations

- **The "Auto" level is not adaptive yet.** The auto-adjust rule (`dnb/difficulty/adjuster.py`)
  is implemented and tested, but the app does not call it yet: "Auto" replays the level of
  your most recent game.
- **The levels are not fully calibrated.** In the arena, Medium (minimax depth 2) is not
  clearly stronger than Easy (greedy), and Beginner was not measured.
- **Reviews only go as deep as the minimax search.** Labels reflect a bounded search, not
  perfect play, and the coaching has not been evaluated with real players.
