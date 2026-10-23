# How we work

Five people, 20 days, one repo. The goal is small, frequent merges that never break `main`.

## Daily loop

```bash
git switch main && git pull
git switch -c p3/elo-rating        # p<your number>/<short-topic>
# ...code + tests...
uv run ruff check . --fix && uv run ruff format . && uv run pytest
git push -u origin p3/elo-rating   # then open a PR on GitHub
```

- **Branch names:** `p<N>/<topic>`, for example `p1/minimax`, `p5/review-screen`.
- **Keep branches short-lived.** Open a PR within 1-2 days, even if the feature isn't finished.
  Unfinished code is fine as long as tests pass and nothing calls it yet.
- **Pull `main` every morning** so your branch never drifts far from everyone else's.
- **Stay in your folder.** If you need a change in someone else's folder, open an issue or ask
  them. Small fixes are fine, but tag the owner on the PR.

## Pull requests

- `main` is protected: nobody pushes to it directly.
- Every PR needs **CI green** and **1 approval**. CODEOWNERS asks the right reviewer
  automatically.
- **Contract changes** (engine API, Bot interface, registry format, API schemas, DB schema) get
  the `contract` label and need **every owner affected** to approve. Announce them in the chat.
- Review within 24 hours. A quick "LGTM" on a small PR is fine.
- Use **squash merge**, so each PR becomes one commit on `main`.

## Tests

- Every module gets tests in `tests/test_<module>.py`.
- Tricky board positions go in `tests/fixtures/` so everyone can test against them.
- The **checkpoint test** (`test_checkpoint_two_random_bots_play_a_full_game`) must never break.
- Tests never call a real LLM. Use `MockProvider`.

## Communication

- **Daily standup** in the group chat, 2 lines: *done yesterday / doing today / blocked?*
- **Weekly integration check** (Person 5): pull `main`, run `scripts/dev.py`, play a full
  game, and post the result.
- **Phase checkpoints** (see docs/ROADMAP.md): the whole team checks them together.

## Secrets

Copy `.env.example` to `.env`. Never commit `.env` or paste API keys into code, issues or chat.
