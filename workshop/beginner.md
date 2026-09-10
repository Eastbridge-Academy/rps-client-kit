# Route A: find a pattern

Start here if Python is new to you, or if you would like a few concrete wins before building a larger model. You can finish a useful bot with a return statement, a small dictionary and a careful choice of history.

## Step 1: a bot that knows one thing

Rocky always plays rock. In bot.py, replace the final line of next_move with:

```python
    return Move.PAPER
```

Keep the spaces at the beginning of the line. In Python, indentation says which statements belong to a function. `return` sends your choice back to the game. It does not print it on the screen.

```bash
rps-cli test
rps-cli play --against rocky --best-of 501
```

You should win **501-0-0** against Rocky, with zero errors. Try returning rock, then scissors. Predict the result before each run and put paper back afterwards. If you get errors, read the first traceback from the tests rather than changing the strategy at random.

## Step 2: make the winning reply reusable

Add this dictionary above next_move, outside the function:

```python
COUNTER = {
    Move.ROCK: Move.PAPER,
    Move.PAPER: Move.SCISSORS,
    Move.SCISSORS: Move.ROCK,
}
```

`COUNTER[Move.ROCK]` looks up the value stored for rock, which is paper. The dictionary is a small table of answers. It is not a prediction yet; you still have to decide which move the opponent is likely to choose.

Try `return COUNTER[Move.ROCK]`. It should behave exactly like the earlier paper bot. This is a useful kind of test: reorganizing code should not accidentally change what it does.

> **Checkpoint:** your bot beats Rocky every throw, and you can explain the difference between a predicted move and the move you actually return.

**Next target:** `cycle_rps` repeats rock, paper, scissors. A constant paper bot has no lasting advantage there. Before writing more code, write its first six moves and a winning reply under each one.
---page---
# Predict the next move

A common mistake is to beat what the opponent just played. Against a repeating cycle, that is one throw too late. If the last move was rock, the next move will be paper, so your reply should be scissors.

## Step 3: follow the cycle

For `cycle_rps`, the next item in the cycle happens to be `COUNTER[last_move]`. Your winning reply is another lookup:

```python
def next_move(my_history, opponent_history, match_state):
    if not opponent_history:
        return Move.PAPER
    prediction = COUNTER[opponent_history[-1]]
    return COUNTER[prediction]
```

The first branch handles the empty history. `if not opponent_history` means there are no completed opposing moves yet. The negative index `[-1]` means the last item, not the item at position one.

```bash
rps-cli play --against cycle_rps --best-of 501
```

For this known bot, the paper opening also wins the first throw. Now change the opening to a random choice. Does one uncertain opening stop the rest of the strategy from working? Count the throws rather than relying on the match's Win label.

## Step 4: a different kind of pattern

Copycat chooses a random opening, then copies **your previous move**. If you played rock last time, its next choice is rock, regardless of what it played itself.

Adapt the prediction line to this opponent. You need `my_history`, not `opponent_history`. Keep the guard for the first throw. Test it on Copycat, then explain why it is not generally a winning strategy against Cycle RPS.

| Completed throw | You played | Copycat played | What will Copycat play next? |
| --- | --- | --- | --- |
| 1 | Rock | Scissors | Write your prediction. |
| 2 | Paper | Rock | Write your prediction. |
| 3 | Scissors | Paper | Write your prediction. |

**Try Echo Two:** this bot copies your move from **two throws ago**. Work out which index you need and how many completed throws you must have before using it. The first two moves are uncertain; judge the strategy after those openings.

> **Checkpoint:** you have tested a cycle predictor and a mimic predictor. You can say whose history each uses and why. Save copies of your working versions before combining them.
---page---
# Put the ideas together

In the tournament you do not get a label telling you that the opponent is Copycat. Your bot must choose a strategy from the evidence in its histories. A rule that wins one practice matchup is a useful experiment, not yet a universal bot.

## Step 5: test a hypothesis before using it

Suppose you want to recognize the cycle. After eight completed throws, check whether each recent move follows the cycle's rule. For a pair of adjacent opposing moves, the check is:

```python
opponent_history[i] == COUNTER[opponent_history[i - 1]]
```

Try this for several adjacent pairs, not just one. A random bot can match a short pattern by accident. If the checks agree, predict the continuation. Otherwise use the random baseline until you have better evidence.

To recognize Copycat, compare `opponent_history[i]` with `my_history[i - 1]` for completed throws after the opening. Be careful: using the same index on both sides tests a different rule. For Echo Two, the gap is two.

You can begin with one detector. Add another only after the first is working. If two hypotheses fit the same short history, keep gathering evidence instead of assuming you have identified the opponent perfectly.

## Step 6: run a small comparison

```bash
rps-cli play --against rocky,cycle_rps,copycat,echo_two
rps-cli play --against random_uniform --games 5 --seed 900
rps-cli validate
```

Keep a small notebook. Give each version a description, such as "paper only" or "cycle detector with eight observations". Record the opponent, seed, throw W-L-D and errors. Change one rule at a time so you can tell which change helped.

| Version | Opponent and seed | Throws W-L-D | What did you learn? |
| --- | --- | --- | --- |
| First working bot |  |  |  |
| One predictor |  |  |  |
| Combined bot |  |  |  |

When a bot fails, distinguish a **Python error** from a **wrong prediction**. Tests and `validate` help with the first. Practice results and saved throws help with the second. Losing to a clever opponent is not a syntax error.

## Finish with a version you understand

Submit under your existing team name and check `status`. Open your match history on the dashboard. Find a place where your prediction was right, and a place where it was wrong. Tell a partner which evidence your bot uses and one opponent you expect to trouble it.

**Optional next step:** the intermediate route replaces exact-pattern checks with counts. It is useful when a bot is biased without repeating perfectly. You already have the hardest habit: separating the opponent's behavior, your prediction and your reply.
