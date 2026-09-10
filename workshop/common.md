# A bot in the arena

Two bots choose rock, paper or scissors without seeing each other's current choice. You write one of them. Your first job is to enter a working bot; the rest of the session is a cycle of making a prediction, testing it and deciding whether the evidence deserves your trust.

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

The setup script uses the supplied kit and dependency wheels. It needs **uv and Python 3.11+**, already prepared on the lab machines. A personal-machine setup is in the bundle README. If you open a new terminal, return to `~/rps-bot` and activate `.venv` again.

Open **bot.py** in your editor. The starter chooses randomly and is already legal. The tests should pass before you change anything. `rps-cli init` can restore missing scaffold files while preserving your bot; `--force` replaces your edits, so use it deliberately.

## Enter early, improve often

Copy the **server URL, league slug and submit token** from the facilitator. The token below is a placeholder, not a real event credential.

```bash
rps-cli config set api_url https://arena.eastbrid.ge
rps-cli config set league rps
rps-cli config set token TOKEN
rps-cli doctor
rps-cli submit "Your Team Name"
rps-cli status "Your Team Name"
```

Use the event's actual league slug if it differs from `rps`. Settings belong to this project folder. Reuse the **same team name** every time you submit. An upload is queued for server validation; `status` tells you when it is active and explains a rejection. Saving bot.py alone does not change the tournament version.

> **First checkpoint:** your tests pass, your project knows the correct event, and you can distinguish an uploaded version from an active one. If setup stalls, ask for help now; your time is better spent building a strategy.

**A two-hour rhythm:** spend the first 20 minutes getting a bot running and understanding the rules. Use about 70 minutes for the route you chose, 20 minutes to test on fresh seeds, and the last 10 to submit and compare notes. Skip optional challenges freely.
---page---
# What your bot sees

The arena imports bot.py into a fresh process for each match. It calls `setup(config)` once if you define it, then calls `next_move(...)` for each throw. The starter has this shape:

```python
from random import Random
from rpsdk import Move

_rng = Random()

def setup(config):
    _rng.seed(config["seed"])

def next_move(my_history, opponent_history, match_state):
    return _rng.choice(list(Move))
```

`Move.ROCK`, `Move.PAPER` and `Move.SCISSORS` are the three choices. `a.beats(b)` is true when a beats b. Returning the lowercase strings also works, but using the enum makes spelling mistakes easier to catch.

## History is evidence, not a preview

Both history lists contain **completed throws, oldest first**. On the first call, both are empty. After two throws, you might see:

```python
my_history       == [Move.ROCK, Move.PAPER]
opponent_history == [Move.SCISSORS, Move.ROCK]
```

You won both of those throws. The next opposing move is still hidden. `opponent_history[-1]` means their last move, while `my_history[-1]` means yours. Guard an empty list before using `[-1]`, and check for at least two elements before using `[-2]`.

| State entry | Meaning |
| --- | --- |
| `round` | Zero-based throw index. The next call above has round 2. |
| `best_of` | Total throws in this match, including draws. |
| `last_outcome` | Your preceding throw's win, loss or draw; None initially. |
| `seed` | Your bot's reproducibility seed. |
| `timeouts`, `opponent_timeouts` | Accumulated server timeouts in this match. |

Learned state and histories reset between matches. If you keep counters in module globals, reset them in setup. Do not seed your generator on every throw; seed it once, then keep drawing from it.

Keep each call quick. Use the standard library and `rpsdk`; your whole virtual environment is not uploaded. Imported local helper modules/packages and files in `data/` are bundled. Open data relative to `Path(__file__).parent`. Avoid network calls, sleeps and large training jobs inside your bot.

> **Check your understanding:** if you want to predict Copycat, which history belongs in the prediction? Its rule is to copy **your** preceding move. The two history arguments are not interchangeable.
---page---
# Why there is room to win

Suppose the opponent always chooses rock. Paper wins every throw. Suppose they choose each move independently with probability one third. Now every move you choose wins one third of the time, loses one third and draws one third. Looking at their previous moves does not change those probabilities.

For the calculations in these sheets, a throw earns **+1 for a win, 0 for a draw, -1 for a loss**. This is a convenient measure of net advantage; the arena determines a match winner by comparing the numbers of throws won.

| Your move | Opponent rock | Opponent paper | Opponent scissors |
| --- | --- | --- | --- |
| Rock | 0 | -1 | +1 |
| Paper | +1 | 0 | -1 |
| Scissors | -1 | +1 | 0 |

## Randomness is a strong baseline

Independent uniform random play remains a Nash equilibrium. Neither player can improve their expected payoff by changing strategy while the other keeps playing that way. More history, a Markov chain, or a clever learning algorithm cannot systematically beat a truly independent uniform opponent.

What changes in this event is the opposition. Some bots favor a move, repeat sequences, react to your history, or change behavior halfway through a match. Those habits make a **conditional prediction** possible. You are looking for evidence of a habit, not a flaw in the equilibrium.

A bot that plays `rock, paper, scissors` repeatedly has perfectly balanced totals after every three throws, yet its next move is predictable. Equal frequencies are not the same as independence. Conversely, a fair random bot can show a streak of rock without having acquired a habit.

The kit uses seeded pseudorandom generators so experiments can be repeated. Treat seeds as experiment controls, not as a way to reverse-engineer another bot's random stream. The mathematical baseline assumes the current random choice is independent and unavailable to the opponent.

## Count the right thing

A **throw** is one simultaneous choice. A **match** is a fixed series, normally 501 throws. A **league round** schedules each pair of bots. Despite the historical name `best_of`, the arena plays the full series; it does not stop at 251 wins. Drawn throws still count, and a 501-throw match can finish level.

If a match ends 290-102, there were 109 drawn throws. The match earns a win for the first bot; a larger margin does not multiply the match result used by the rating system. Local practice shows both match results and throw totals, not Elo.

```bash
rps-cli play --against random_uniform --games 5 --seed 100
```

> **Before trusting an improvement:** run several fresh seeds, keep the series length fixed, inspect errors, and compare more than one opponent. One lucky match against random play is not evidence of an exploit. Reserve seeds you did not use while tuning.
