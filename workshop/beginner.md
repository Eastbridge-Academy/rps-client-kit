# Route A: find a pattern

Start here if you're new to Python. We'll first beat a bot that always plays rock, then try a few opponents whose moves follow a rule. Along the way you'll use return statements, dictionaries and the two history lists.

## Step 1: beat Rocky

Rocky always plays rock. In bot.py, replace the final line of next_move with:

```python
    return Move.PAPER
```

Keep the spaces at the beginning of the line. In Python, indentation says which statements belong to a function. `return` sends your choice back to the game. It does not print it on the screen.

```bash
rps-cli test
rps-cli play --against rocky --best-of 501
```

You should win **501-0-0** against Rocky, with zero errors. Try returning rock, then scissors. Predict the score before each run and put paper back afterwards. If a test fails, its traceback gives the line where Python ran into trouble.

## Step 2: a dictionary of replies

Add this dictionary above next_move, outside the function:

```python
COUNTER = {
    Move.ROCK: Move.PAPER,
    Move.PAPER: Move.SCISSORS,
    Move.SCISSORS: Move.ROCK,
}
```

`COUNTER[Move.ROCK]` looks up the value stored for rock, which is paper. Once you've guessed what the opponent will play, this dictionary gives you the move that beats it.

Try `return COUNTER[Move.ROCK]` and run the Rocky match again. You should get the same score as before.

> **Check:** what do `COUNTER[Move.PAPER]` and `COUNTER[Move.SCISSORS]` return? Run each against Rocky. Can you account for the scores?

**Next opponent:** `cycle_rps` repeats rock, paper, scissors. Write its first six moves and a winning reply under each one. How would your paper-only bot do?
---page---
# Predict the next move

Cycle RPS moves on after every throw. If it just played rock, it's about to play paper, so you'll need scissors. Let's use the last move to work out the next one.

## Step 3: follow the cycle

For `cycle_rps`, the next item in the cycle happens to be `COUNTER[last_move]`. Your winning reply is another lookup:

```python
def next_move(my_history, opponent_history, match_state):
    if not opponent_history:
        return Move.PAPER
    prediction = COUNTER[opponent_history[-1]]
    return COUNTER[prediction]
```

The first branch handles the empty history: `if not opponent_history` is true before any throws have finished. Later calls use `[-1]`, Python's index for the last item in a list.

```bash
rps-cli play --against cycle_rps --best-of 501
```

Cycle RPS opens with rock, so paper wins the first throw too. Now change your opening to a random choice and run it again. How many throws did that change affect?

## Step 4: play Copycat

Copycat chooses a random opening, then copies **your previous move**. If you played rock last time, its next choice is rock, regardless of what it played itself.

Change the prediction line to use `my_history`. Keep the opening branch, since Copycat's first move is random. Test the result on Copycat, then run the same bot against Cycle RPS. Where does its prediction go wrong?

| Completed throw | You played | Copycat played | What will Copycat play next? |
| --- | --- | --- | --- |
| 1 | Rock | Scissors |  |
| 2 | Paper | Rock |  |
| 3 | Scissors | Paper |  |

**Try Echo Two:** this bot copies your move from **two throws ago**. Which index will you need? How many entries must the history have before you can use it? Look at the score after the first two throws, once Echo Two has something to copy.

> **Save your work:** keep a copy of each bot that works. Label it with the opponent it was written for; you'll combine these ideas on the next page.
---page---
# Recognizing an opponent

The tournament doesn't tell next_move which opponent it's facing. To choose between your cycle and Copycat strategies, you'll have to inspect the moves played so far.

## Step 5: look for the cycle

Suppose you want to recognize the cycle. After eight completed throws, check whether each recent move follows the cycle's rule. For a pair of adjacent opposing moves, the check is:

```python
opponent_history[i] == COUNTER[opponent_history[i - 1]]
```

Check several adjacent pairs: a random bot can match a short pattern by accident. If the checks agree, predict the continuation. Otherwise keep the random baseline.

For Copycat, compare `opponent_history[i]` with `my_history[i - 1]` after the opening. The offset matters because Copycat copies your preceding throw. For Echo Two, use a gap of two instead.

Start with one working detector. If two hypotheses fit the same short history, gather more evidence before choosing between them.

## Step 6: run a small comparison

```bash
rps-cli play --against rocky,cycle_rps,copycat,echo_two
rps-cli play --against random_uniform --games 5 --seed 900
rps-cli validate
```

Describe each version in a notebook: "paper only" or "cycle detector with eight observations". Record the opponent, seed, throw W-L-D and errors. Change one rule at a time.

| Version | Opponent and seed | Throws W-L-D | What did you learn? |
| --- | --- | --- | --- |
| First working bot |  |  |  |
| One predictor |  |  |  |
| Combined bot |  |  |  |

If the bot reports errors, run the tests and `validate` to find the problem. If it runs normally but loses, inspect a few throws where its prediction was wrong. Which rule was it using?

## Submit your latest version

Submit under your existing team name and check `status`. Open a match on the dashboard and walk through a few throws with a partner. Show them how your bot chose its move, including any guesses that went wrong.

**Want to try another route?** The intermediate packet uses counts to predict bots that favor certain moves without repeating an exact pattern.
