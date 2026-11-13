# Person 3 – Adaptive Difficulty System

## Overview

The objective of Person 3's contribution was to implement an adaptive difficulty system for the Dots and Boxes AI game. The system adjusts the AI difficulty based on the player's recent performance, providing a more balanced and personalized gameplay experience.

The implementation consists of an Elo rating system, automatic difficulty adjustment, five predefined difficulty levels, and player performance statistics.

## Difficulty Levels

Five difficulty levels were defined, each corresponding to a different AI bot configuration.

| Level | Difficulty | Bot Configuration |
|---|---|---|
| 1 | Beginner | Greedy with 0.5 randomness |
| 2 | Easy | Greedy |
| 3 | Medium | Minimax (depth 2) |
| 4 | Hard | Minimax (depth 4) |
| 5 | Expert | Monte Carlo (2000 simulations, greedy playouts) |

These configurations allow the game to offer progressively stronger AI opponents.

## Elo Rating System

An Elo-based rating system was implemented to estimate player strength based on match outcomes.

The expected score is calculated using:

\[
E_A = \frac{1}{1+10^{(R_B-R_A)/400}}
\]

The rating is updated using:

\[
R'_A = R_A + K(S_A-E_A)
\]

Where:

- \(R_A\) and \(R_B\) represent the ratings of the two players.
- \(E_A\) is the expected score.
- \(S_A\) is the actual match score.
- \(K\) is the rating adjustment factor.

This allows player ratings to increase or decrease depending on match performance.

## Automatic Difficulty Adjustment

An adaptive difficulty adjuster was implemented to analyze the player's **five most recent game outcomes**.

- Recent wins and losses are evaluated to determine whether the difficulty should change.
- Difficulty is increased or decreased based on predefined performance thresholds.
- The difficulty level is restricted to the range of **1 to 5**.
- If there are insufficient match results, the current difficulty level is maintained.

This helps the game respond dynamically to changes in player performance.

## Player Statistics

A player statistics module was implemented to calculate and track the following information:

1. Total games played.
2. Win rate.
3. Boxes given away per game.
4. Elo rating.
5. Current difficulty level.

The `compute_stats()` function retrieves and calculates player performance information using the project's database.

## Implementation Files

The following files were developed as part of Person 3's contribution:

**Core implementation**
- `dnb/difficulty/elo.py`
- `dnb/difficulty/adjuster.py`
- `dnb/difficulty/levels.py`
- `dnb/difficulty/stats.py`

**Unit tests**
- `tests/test_elo.py`
- `tests/test_adjuster.py`
- `tests/test_levels.py`
- `tests/test_stats.py`

## Testing and Results

Unit tests were written to validate the individual components of the adaptive difficulty system.

| Test Module | Tests Passed |
|---|---:|
| Elo rating | 10 |
| Difficulty adjuster | 12 |
| Difficulty levels | 19 |
| Player statistics | 6 |
| **Total** | **47/47** |

The complete project test suite was also executed successfully.

- **Dedicated Person 3 tests:** 47 passed.
- **Full project test suite:** 175 passed.
- **Full suite execution time:** 4.02 seconds.

## GitHub Contribution

The implementation was submitted through a dedicated feature branch:

`person3-adaptive-difficulty`

The initial contribution included eight project files and was submitted through Pull Request #3:

**Implement Person 3 Adaptive Difficulty System**

## Conclusion

The adaptive difficulty module provides a foundation for personalized gameplay in Dots and Boxes AI. By combining Elo-based ratings, performance-driven difficulty adjustment, predefined bot configurations, and player statistics, the system aims to maintain an appropriate challenge for players of different skill levels.

Further integration with the bot arena, game history, and player profile components will allow the adaptive system to operate as part of the complete application.