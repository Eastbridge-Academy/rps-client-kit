# Route B: estimate and adapt

A biased opponent does not need to repeat a fixed pattern. If it plays rock 60% of the time, paper 25% and scissors 15%, paper has expected net payoff `0.60 - 0.15 = +0.45` per throw. A noisy observation can still be useful.

## Step 1: count what you have seen

Use `collections.Counter` to count moves in opponent_history. Choose a random move while the history is empty. Then build a response from those counts:

```python
from collections import Counter

counts = Counter(opponent_history)
values = {
    Move.ROCK: counts[Move.SCISSORS] - counts[Move.PAPER],
    Move.PAPER: counts[Move.ROCK] - counts[Move.SCISSORS],
    Move.SCISSORS: counts[Move.PAPER] - counts[Move.ROCK],
}
```

The numbers are estimated wins minus losses, up to a common factor. Dividing each by the number of observations would give estimated net payoff per throw, but would not change which is largest. When several moves tie, choose randomly among the tied moves.

Do not automatically counter the most frequent move. If the distribution is **40% rock, 21% paper, 39% scissors**, paper's expected payoff is only +0.01, while rock's is +0.18. Rock exploits the abundant scissors without losing often to paper.

> **Paper check:** calculate all three expected payoffs for that distribution using the shared payoff table. Then explain why prediction accuracy and playing strength are different objectives.

## Step 2: establish a baseline

```bash
rps-cli play --against biased_random --games 5 --seed 100
rps-cli play --against random_uniform --games 5 --seed 100
```

The first opponent has a genuine bias. The second is your calibration control. An early imbalance against Random Uniform can be ordinary noise, so compare fresh seeds before declaring that your estimator has found a weakness.

Add a modest observation threshold before committing strongly. Try thresholds such as 5, 15 and 30, and keep the rest of your code unchanged. A larger threshold trades slower exploitation for more evidence; it does not certify that the distribution is stationary.
---page---
# When the past goes stale

Switcheroo plays rock for the first half of the series and scissors afterwards. An all-history count can keep recommending paper long after that has become a losing reply. Your observations are accurate; the assumption that they all describe the present is wrong.

## Step 3: shorten the memory

Start with a rolling window:

```python
window = opponent_history[-30:]
counts = Counter(window)
```

The payoff calculation is unchanged. Compare windows of 10, 30 and 100. A short window reacts quickly but has more sampling noise. A long window estimates a fixed bias more smoothly but carries old behavior across a change.

```bash
rps-cli play --against switcheroo,shifting_bias --games 5 --seed 200
rps-cli play --against biased_random --games 5 --seed 200
```

Shifting Bias changes its favored move every 50 throws; the favorite has probability 70%, and the others 15% each. Its initial favorite varies with the seed. Watching how long your bot takes to recover after a switch is more informative than a single final score.

## Step 4: inspect the change

```bash
rps-cli play --against shifting_bias --seed 200 --output drift.json
```

The JSON file contains a list of matches, each with its seed, totals and every observed throw. Each throw has a zero-based `round`, your move, the opposing move, a +1/0/-1 `outcome`, and any local error.

Read the first match in a small Python script:

```python
import json
from pathlib import Path
match = json.loads(Path("drift.json").read_text())["matches"][0]
for start in range(0, len(match["rounds"]), 50):
    block = match["rounds"][start:start + 50]
    print(start, sum(row["outcome"] for row in block))
```

The final block may contain only one throw in a 501-throw match. Do not compare its raw total to a full 50-throw block as if they had equal length; divide by the number of throws when needed.

> **Checkpoint:** identify one opponent where forgetting helps and one where it hurts. Describe the tradeoff in terms of changing behavior and noisy samples, rather than saying that one window is always best.
---page---
# Condition on something useful

Sticky is balanced in the long run, yet it repeats its previous move with probability 0.8. The other two moves each have probability 0.1. If its last move was rock, paper has expected net payoff `0.8 - 0.1 = +0.7` on the next throw.

## Step 5: separate total counts from conditional counts

Try countering Sticky's last move. Compare this with the frequency-only bot. The first uses the condition "its last move was rock"; the second mixes together all three situations and can lose the useful information.

Now inspect **Win Stay Lose Shift**. It repeats after a win **or a draw**, and after a loss chooses uniformly between the two other moves. You can reconstruct its previous outcome from the histories:

```python
opponent_won = opponent_history[-1].beats(my_history[-1])
drawn = opponent_history[-1] == my_history[-1]
```

These lines require a nonempty history. `match_state["last_outcome"]` is from **your** perspective, so your win means its loss.

If the opponent just lost with rock, it will next choose paper or scissors. Your best reply is scissors: it wins against paper and draws against scissors. Playing rock would win once and lose once on average. Work out the corresponding replies after losses with paper and scissors.

## Step 6: predict a reactive opponent

Contrarian always counters your previous move after its opening. If you played rock, it will choose paper, so your reply should be scissors. This is another case where the useful evidence is in **my_history**.

```bash
rps-cli play --against sticky,win_stay_lose_shift,contrarian
```

A hand-written response to a named house bot is a good way to test understanding. In the tournament, deciding **when that model applies** is another problem. Compare how many recent observations agree with each rule, and keep a fallback for cases where none fits.

> **Checkpoint:** for each of the three opponents above, state the condition your predictor uses. Explain why one universal rule such as "counter the last opposing move" does not solve all three.

**Optional bridge to the next route:** instead of encoding Sticky's repeat probability, learn three separate tables, one for each last opposing move. That is a first-order Markov model.
---page---
# Make the comparison fair

By now you may have several plausible policies: all-history counts, a short window, a reactive rule and a random fallback. The temptation is to keep whichever won the most recent game. That also selects lucky runs.

## Step 7: reserve a test set

Use one group of seeds while designing your strategy and another group for the final comparison. For example, tune on 100 through 104, then test on 900 through 904. Keep the opponents and series length the same for both versions.

```bash
rps-cli play --against biased_random,shifting_bias,sticky \
  --best-of 501 --games 5 --seed 900 --output test-set.json
```

Every match starts with a fresh process and fresh learned state. You cannot carry a table learned against one opponent into the next match. If your bot uses global counters, reset them in setup so unit tests and other local uses also start correctly.

| Policy | Fixed bias | Changing bias | Reactive bot | Uniform control |
| --- | --- | --- | --- | --- |
| All-history counts |  |  |  |  |
| Recent window |  |  |  |  |
| Your combined policy |  |  |  |  |

For each column, record both **match W-L-D** and average **net payoff per throw**. They answer different questions. A huge win over one weak bot does not cancel a match loss to every other bot in the same way that pooled throw totals suggest.

## Step 8: add uncertainty without making promises

One simple experiment is to use your learned policy on 80% of throws and the uniform baseline on the rest. This makes your own behavior less rigid, but it can also throw away a real advantage. Compare it; do not assume the word "random" makes it safer in every sense.

If you try many windows, thresholds and mixtures on the same seeds, those seeds become part of training. Use a genuinely new batch for your final check. Random fluctuations and opponent adaptation mean a short local score is evidence with limits, not a guarantee.

## Submit a version you can defend

Run `rps-cli test` and `rps-cli validate`, then submit under your existing team name and check that the latest version is active. Keep your earlier working bot available in case an ambitious change introduces an error near the end.

> **Final discussion:** which assumption does your bot make about the opponent, what observation would contradict it, and how quickly would your policy respond? A clear answer is more useful than an unexplained leaderboard position.
