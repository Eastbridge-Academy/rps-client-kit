# Route C: learn the dependency

A frequency table asks how often each move occurs. A first-order Markov model asks a more specific question: **what tends to follow the opponent's last move?** Sticky and Cycle RPS are good first targets because their next moves depend strongly on that context.

## Step 1: build a transition table

For the observed sequence `R, R, P, R, S`, count `R->R`, `R->P`, `P->R` and `R->S`. The table has a row for the preceding move and a column for the following move.

```python
from collections import Counter

transitions = {move: Counter() for move in Move}
for previous, following in zip(history, history[1:]):
    transitions[previous][following] += 1
```

Here `history` is a completed opponent history. This rebuilds the table from scratch, which is a clear reference implementation. At 501 throws it is small enough to test; an incremental implementation should agree with it exactly.

On the next call, look up the row for `opponent_history[-1]`. With no history, use uniform random play. With an unseen context, back off to overall counts or the uniform baseline.

## Step 2: choose by payoff

Turn the selected row into estimated probabilities. Add one pseudo-observation to each move if you want Laplace smoothing:

```python
row = transitions[opponent_history[-1]]
total = sum(row.values()) + 3
q = {move: (row[move] + 1) / total for move in Move}
values = {
    Move.ROCK: q[Move.SCISSORS] - q[Move.PAPER],
    Move.PAPER: q[Move.ROCK] - q[Move.SCISSORS],
    Move.SCISSORS: q[Move.PAPER] - q[Move.ROCK],
}
```

Choose a maximum-payoff move, randomizing ties. Countering the most likely move is not always equivalent: check the intermediate route's 40% rock, 21% paper, 39% scissors example.

> **Checkpoint:** hand-count the transition row for rock in `R,R,P,R,S`, then compare it with your code. Test both an empty history and a history whose final context has never had a successor.
---page---
# A pattern hidden from first order

Double Take repeats a nine-throw sequence, with a seed-dependent starting phase:

```text
R R P R S P P S S   (then wrap around)
```

Each move appears three times. Each ordered adjacent pair appears once per cycle, including the wraparound pair. A table conditioned on only one previous move therefore looks uniform over complete cycles. Yet the next move is deterministic once you know the preceding **two** moves.

## Step 3: increase the context

Use a tuple as the dictionary key:

```python
counts = {}
for i in range(2, len(history)):
    context = tuple(history[i - 2:i])
    counts.setdefault(context, Counter())[history[i]] += 1
```

For the next prediction, the context is `tuple(history[-2:])`. Again, this snippet rebuilds the counts for clarity. It counts only successors that were already observed, never an unseen continuation of the current suffix.

Try order one and order two against the same seeds of Double Take. Inspect the early throws separately from the settled part of the match. A model must see a context and its successor before it can learn that relationship.

## Step 4: control the cost of a larger model

An order-$k$ model has up to $3^k$ contexts before considering your own moves. With 501 throws, long contexts are often seen once or not at all. A model can memorize its observations without predicting well.

Use a backoff ladder: a supported order-two row, otherwise order one, otherwise overall counts, otherwise uniform. Try requiring two or three observations in a context before trusting it. Compare the delayed learning against reduced confidence in accidental patterns.

```bash
rps-cli play --against double_take,cycle_rps,sticky \
  --games 5 --seed 300
rps-cli play --against random_uniform --games 5 --seed 700
```

> **Paper challenge:** list the nine cyclic adjacent pairs. For each pair, write its next move. This gives you a complete order-two predictor without relying on the bot's seed or its absolute turn index.

**Optional optimization:** update exactly one completed transition at each call. For order two, once three moves exist, increment the row keyed by `history[-3:-1]` with successor `history[-1]`. Do not add the whole history to persistent counts on every call; that repeatedly counts old data.
---page---
# The opponent can learn too

A good next-move model is not a permanent identification of the opponent. Markov learns your transitions. Sequence Hunter searches for repeated suffixes. Adaptive Ensemble switches among several predictors according to recent accuracy. Your own choices can change what these bots do next.

## Step 5: score predictions before learning the answer

Keep the distribution that each model predicted **on the previous call**. When the next completed opposing throw arrives, evaluate those stored predictions, then update the models. Recomputing yesterday's prediction after seeing today's answer leaks information into your score.

One scoring option is log loss: `-log(max(q[observed_move], epsilon))`. A confidently wrong prediction is penalized more than a cautious one. Another is the virtual payoff of the action or action distribution the model recommended. These are different objectives, so say which one you are optimizing.

Use a test sequence you wrote by hand. Record what the predictor knew at each call. Verify that changing a later element of the sequence cannot change an earlier prediction.

## Step 6: compare models rather than guessing one

Try a small pool: overall counts, a recent window, order one, order two and a reactive predictor based on your own history. Retain a uniform fallback. Start by choosing the model with the best recent score; the expert route explores smoother weighting.

Be precise about a reactive model. Copycat's next move depends on your previous move, while a transition model of the opponent alone uses its own previous move. A joint context can express both, but it increases the number of states and the amount of data needed.

```bash
rps-cli play --against markov,sequence_hunter,adaptive_ensemble \
  --games 5 --seed 500 --output learners.json
```

Watch for a predictor that wins early and loses later. Is the opponent adapting to you, is your window too slow, or did your model merely fit a short accidental pattern? Change one feature, then rerun on new seeds.

> **Checkpoint:** explain exactly when each stored prediction is produced and when it is scored. Your explanation should still be correct on the first call, after a draw, and after a model has no matching context.

**Optional challenge:** compare a model that predicts the opponent from your own last two moves with one that predicts from its last two. Which house personalities make the distinction matter?
---page---
# Validate the model, then the bot

A passing contract test does not establish that a Markov model is correct. A winning match does not establish that the model learned what you think it learned. Use small deterministic examples for the model and fresh-seed matches for the policy.

## Step 7: write diagnostic tests

Test at least these cases:

- Empty history and an unseen context both produce a legal fallback.
- The transition counts for a short written sequence match your hand calculation.
- Your incremental table matches a full rebuild after every new observation.
- A complete Double Take cycle gives balanced order-one rows but deterministic order-two continuations.
- Calling setup again clears learned state.

Keep the model helper functions separate from next_move if that makes them easier to test. `rps-cli test -k transition` can run tests whose names contain transition. The submission packager follows imported local modules and packages; `rps-cli package` lets you inspect the exact archive without uploading it.

## Step 8: make an ablation table

Compare variants with one feature removed, rather than comparing only an elaborate final bot with a weak baseline.

| Variant | Cycle RPS | Sticky | Double Take | Shifting Bias | Uniform |
| --- | --- | --- | --- | --- | --- |
| Frequency only |  |  |  |  |  |
| Order one |  |  |  |  |  |
| Order two + backoff |  |  |  |  |  |
| Your final policy |  |  |  |  |  |

Use the same held-out seeds and 501 throws for every variant. Report match W-L-D as well as mean net payoff per throw. A confidence interval computed as though all throws were independent is not justified for a reactive match; independent seeded matches are a more useful experimental unit.

## Keep the implementation small enough to finish

A few counters and small dictionaries are sufficient for these models. The lab machines are Raspberry Pi 5s: avoid rebuilding enormous feature matrices or training a large model inside every call. If an optimization changes results, first find the correctness difference with a tiny sequence.

> **Final checkpoint:** your bot is active in the arena, your model passes a hand-checkable test, and your held-out comparison identifies both a strength and a weakness. Describe the dependency it learned, not just the name of the algorithm.
