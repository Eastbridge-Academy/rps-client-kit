# A bot in the arena

You'll write a Python bot that plays rock, paper, scissors against everyone else's bots. Both players choose at the same time. We'll start by entering the supplied random bot, then spend most of the session changing how it plays.

## Start with a working project

On the lab machines, your facilitator provides **rps-event-kit** in your home folder. Open a terminal and run:

```bash
cd ~/rps-event-kit
./start.sh ~/rps-bot
cd ~/rps-bot
source .venv/bin/activate
rps-cli test
rps-cli validate
```

These commands install the kit and its dependencies from the supplied folder. **uv and Python 3.11+** are already installed on the lab machines; for your own computer, see the bundle README. Whenever you open a new terminal, return to `~/rps-bot` and activate `.venv` again.

Open **bot.py** in your editor. It currently chooses a random move, and its tests should pass as supplied. If you accidentally delete a starter file, `rps-cli init` will restore missing files. Adding `--force` also overwrites files you've edited.

## Submit your bot

Your facilitator will give you the **server URL, league slug and submit token**. Substitute those values in the commands below, including replacing `TOKEN` with the supplied token.

```bash
rps-cli config set api_url https://arena.eastbrid.ge
rps-cli config set league rps
rps-cli config set token TOKEN
rps-cli doctor
rps-cli submit "Your Team Name"
rps-cli status "Your Team Name"
```

The settings are saved in your project folder. Reuse the **same team name** for later submissions so they replace your earlier version. The server checks each upload before letting it play; `status` shows when it becomes active, or why it was rejected. Run `submit` again whenever you want the tournament to use your latest edits.

> **Before moving on:** run `status` and find your active version. If you're stuck on installation or submission, ask a facilitator to take a look.

---page---
# What your bot sees

For each match, the arena starts a fresh Python process and imports bot.py. It calls `setup(config)` once, if you've defined it, then asks `next_move(...)` for each throw. Here is the starter bot:

```python
from random import Random
from rpsdk import Move

_rng = Random()

def setup(config):
    _rng.seed(config["seed"])

def next_move(my_history, opponent_history, match_state):
    return _rng.choice(list(Move))
```

Return `Move.ROCK`, `Move.PAPER` or `Move.SCISSORS` from next_move. These values also have a comparison method: `a.beats(b)` tells you whether a beats b. The arena accepts lowercase strings too, though the named values help catch spelling mistakes.

## Reading the histories

Both history lists contain **completed throws, oldest first**. On the first call, both are empty. After two throws, you might see:

```python
my_history       == [Move.ROCK, Move.PAPER]
opponent_history == [Move.SCISSORS, Move.ROCK]
```

You won both of those throws. `opponent_history[-1]` gives their last move, while `my_history[-1]` gives yours. Check that a list has an entry before using `[-1]`, or two entries before using `[-2]`. The histories never include the throw you're about to choose.

| State entry | Meaning |
| --- | --- |
| `round` | Zero-based throw index. The next call above has round 2. |
| `best_of` | Total throws in this match, including draws. |
| `last_outcome` | Your preceding throw's win, loss or draw; None initially. |
| `seed` | Your bot's reproducibility seed. |
| `timeouts`, `opponent_timeouts` | Accumulated server timeouts in this match. |

Each match starts with empty histories and fresh learned state. Reset any global counters in setup so your bot also works when tests call setup repeatedly. Seed the random generator there once; next_move can then draw from it throughout the match.

> **Try it on paper:** Copycat copies your preceding move. Given the two histories above, what will it play next? Which history did you use?
---page---
# Can you beat random play?

Against a bot that always chooses rock, you can win every throw by choosing paper. Against one that chooses each move independently with probability one third, any move you pick wins, loses and draws with equal probability. Its previous moves give you no help with the next one.

We'll calculate payoff as **+1 for a win, 0 for a draw, -1 for a loss**. Adding those values over a match gives your wins minus your losses. Whoever wins more throws wins the match.

| Your move | Opponent rock | Opponent paper | Opponent scissors |
| --- | --- | --- | --- |
| Rock | 0 | -1 | +1 |
| Paper | +1 | 0 | -1 |
| Scissors | -1 | +1 | 0 |

## The Nash equilibrium

When both players choose independently and uniformly, neither can improve their expected payoff by changing strategy alone. This is a **Nash equilibrium**. Even a bot with the full match history and a very good prediction algorithm has expected net payoff zero against an independent uniform opponent.

Several house bots do something more predictable. One favors rock; another repeats a sequence; Copycat copies your last move. You can use those habits to predict what comes next and choose a winning reply. Much of the workshop is about learning to recognize them from a short history.

A repeating `rock, paper, scissors` bot is an especially helpful example. Count its moves after any complete cycle and you'll find equal totals. But once you've seen rock, you know paper is coming. A random bot can also produce that sequence by chance, so you'll need more than one occurrence before treating it as a pattern.

The kit uses seeded pseudorandom generators to make practice matches repeatable. The exercises use those seeds to compare versions under the same conditions. They assume each bot's current random choice is private; reconstructing an opponent's generator from its seed would be a different problem.

---page---
# Practice matches

You can play practice matches on your own machine while your submitted bot competes in the arena. Save a copy before trying a new strategy, so you can compare the two versions or go back to the earlier one.

## Reading the score

A **throw** is one simultaneous choice. A **match** is a fixed series, normally 501 throws. A **league round** schedules each pair of bots. Despite the historical name `best_of`, the arena plays the full series; it does not stop at 251 wins. Drawn throws still count, and a 501-throw match can finish level.

For example, a 501-throw match ending 290-102 had 109 draws. The rating system records a match win for the first bot, regardless of the size of that margin. Local practice reports match results and throw totals; ratings belong to the arena.

```bash
rps-cli play --against random_uniform --games 5 --seed 100
```

> **Comparing versions:** use the same opponents, seeds and series length for both bots. Once you've chosen a version, try it on some fresh seeds as well. Check the error counts before you read much into the score.

## What gets uploaded

Your upload includes the installed `rpsdk`, imported local helper modules and packages, and files in `data/`. Other packages from your virtual environment are left out, so use the standard library for these exercises. Open data files relative to `Path(__file__).parent`. Each move has a time limit; network calls, sleeps and large training jobs are likely to exceed it.

## During the session

Allow about 20 minutes for setup and the rules, then 70 minutes for your chosen route. Leave another 20 minutes to test your final version on fresh seeds and 10 to submit it. You can skip an optional exercise or switch routes whenever you like.
