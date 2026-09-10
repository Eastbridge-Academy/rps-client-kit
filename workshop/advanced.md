# Route C: Markov models

A first-order Markov model estimates **what tends to follow the opponent's last move**. You'll build one table for throws after rock, one for throws after paper, and one for throws after scissors. Start with Sticky and Cycle RPS, whose previous moves give you a lot to work with.

## Step 1: build a transition table

For the observed sequence `R, R, P, R, S`, count `R->R`, `R->P`, `P->R` and `R->S`. The table has a row for the preceding move and a column for the following move.

```python
from collections import Counter

transitions = {move: Counter() for move in Move}
for previous, following in zip(history, history[1:]):
    transitions[previous][following] += 1
```

Here `history` is a completed opponent history. The loop rebuilds the table on every call. That's manageable for 501 throws, and it gives you a version to check against if you later update just one count per call.

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

Choose a move with the largest value, randomizing ties. Try the calculation for 40% rock, 21% paper and 39% scissors: rock has the highest expected payoff, even though paper beats the most common move.

> **Check:** count the transitions out of rock in `R,R,P,R,S` by hand, then compare with your code. What does your bot do with an empty history? What happens when the last move has never appeared earlier in the history?
---page---
# Remembering two moves

Double Take repeats a nine-throw sequence, with a seed-dependent starting phase:

```text
R R P R S P P S S   (then wrap around)
```

Each move appears three times. Each ordered adjacent pair appears once per cycle, including the pair across the end and beginning. Over complete cycles, your first-order rows will all look uniform. Try looking at the preceding **two** moves: each pair always has the same successor.

## Step 3: increase the context

Use a tuple as the dictionary key:

```python
counts = {}
for i in range(2, len(history)):
    context = tuple(history[i - 2:i])
    counts.setdefault(context, Counter())[history[i]] += 1
```

For the next prediction, look up `tuple(history[-2:])`. The loop above counts completed observations. The final pair in the history has no successor yet, so it contributes no new count on this call.

Run order one and order two against Double Take with the same seeds. Look at the opening throws as well as the final score. How many observations does the order-two bot need before it starts winning consistently?

## Step 4: handle sparse counts

An order-$k$ model has up to $3^k$ contexts, even before you include your own moves. At order six that's 729 contexts for a match with just 501 throws. Many rows will be empty, and others will contain only one observation.

When an order-two row has too few observations, use order one, then overall counts, then uniform play if necessary. This is called **backoff**. Try requiring two or three observations before using a row. How much does that delay learning, and does it reduce mistakes from chance patterns?

```bash
rps-cli play --against double_take,cycle_rps,sticky \
  --games 5 --seed 300
rps-cli play --against random_uniform --games 5 --seed 700
```

> **Paper challenge:** list the nine adjacent pairs, including the one across the end of the cycle. Write the next move beside each pair, then use the table to predict a cycle starting at a different position.

**Optional optimization:** update exactly one completed transition at each call. For order two, once three moves exist, increment the row keyed by `history[-3:-1]` with successor `history[-1]`. Do not add the whole history to persistent counts on every call; that repeatedly counts old data.
---page---
# The opponent can learn too

Some house bots learn from you. Markov counts your transitions, Sequence Hunter looks for repeated sequences in your history, and Adaptive Ensemble switches predictors as their accuracy changes. A strategy that beats one of these bots early in a match may stop working as it adapts.

## Step 5: score each prediction

Store each model's predicted distribution **when it makes the prediction**. On the next call, score that saved distribution against the newly completed throw, then update the model. If you update first and recompute the prediction, the model gets to use the answer in its own assessment.

One scoring option is log loss: `-log(max(q[observed_move], epsilon))`. It penalizes a model heavily when it assigned very little probability to the move that occurred. You can also score the payoff of the move or distribution it recommended. Choose which score you want to optimize before comparing models.

Use a test sequence you wrote by hand. Record what the predictor knew at each call. Verify that changing a later element of the sequence cannot change an earlier prediction.

## Step 6: choose among models

Keep scores for overall counts, a recent window, order one, order two and a predictor based on your own history. Use the best recent scorer to choose your move, with uniform play as a fallback. The expert route shows how to weight several models at once.

For Copycat, the relevant context is your previous move. Your transition table so far uses the opponent's previous move. You could include both in the key, though the extra contexts will need more observations to fill.

```bash
rps-cli play --against markov,sequence_hunter,adaptive_ensemble \
  --games 5 --seed 500 --output learners.json
```

If a bot wins early and loses later, inspect the predictions around the change. Try shortening its window or removing a predictor, then rerun on new seeds to see whether that helps.

> **Check the timing:** trace the first three calls to your bot on paper. Mark when a prediction is saved, scored and updated. Include a drawn throw and a context the model hasn't seen before.

**Optional challenge:** compare a model that predicts the opponent from your own last two moves with one that predicts from its last two. Which house personalities make the distinction matter?
---page---
# Testing a Markov bot

The starter tests check that your bot returns legal moves. Add a few tests for the counts and prediction updates you've written, using sequences short enough to work through by hand. Then test the complete bot in practice matches.

## Step 7: test the model

Test at least these cases:

- Empty history and an unseen context both produce a legal fallback.
- The transition counts for a short written sequence match your hand calculation.
- Your incremental table matches a full rebuild after every new observation.
- A complete Double Take cycle gives balanced order-one rows but deterministic order-two continuations.
- Calling setup again clears learned state.

Keep the model helper functions separate from next_move if that makes them easier to test. `rps-cli test -k transition` can run tests whose names contain transition. The submission packager follows imported local modules and packages; `rps-cli package` lets you inspect the exact archive without uploading it.

## Step 8: make an ablation table

Remove one feature at a time and record how the results change. This is an **ablation**: it helps you find out which parts of your bot are earning their keep.

| Variant | Cycle RPS | Sticky | Double Take | Shifting Bias | Uniform |
| --- | --- | --- | --- | --- | --- |
| Frequency only |  |  |  |  |  |
| Order one |  |  |  |  |  |
| Order two + backoff |  |  |  |  |  |
| Your final policy |  |  |  |  |  |

Use the same held-out seeds and 501 throws for every variant. Report match W-L-D as well as mean net payoff per throw. For uncertainty estimates, treat independently seeded matches as the samples. Throws within a reactive match depend on one another, so an interval that assumes 501 independent observations may be misleading.

> **Before you finish:** submit the tested version and confirm that it's active. Show a partner your ablation table and a sequence your bot learned to predict. Which feature made the biggest difference?
