# Route D: compete with your models

Treat the match as a short online decision problem. You have a catalogue of plausible policies, none reliable everywhere, and only 501 observations before state resets. The useful question is not which policy sounds most sophisticated, but how to allocate trust while keeping the experiment interpretable.

## Experiment 1: an expert portfolio

Build a small set of policies that each return an **action distribution** over rock, paper and scissors. Include uniform play, a frequency response, a short-window response, order-one and order-two responses, and one or two reactive models. A deterministic recommendation is a one-hot distribution.

Before throw t, expert i proposes `p_i,t`. Give it weight `w_i,t`, normalize the weights, and sample your actual move from their weighted mixture. Store every proposed distribution before the opposing move is revealed.

After observing opposing move b, you can compute the one-step virtual gain of **every** proposal:

```text
g_i,t = sum over actions a of p_i,t(a) * payoff(a, b)
```

This is full-information feedback for the current realized opposing move; you are not limited to the payoff of the move you happened to sample. Score the stored proposals, then update their models for the next throw.

An exponential update is `w_i,t+1 = w_i,t * exp(eta * g_i,t)`. Start with equal positive weights. Use log weights and subtract the maximum before exponentiating to keep normalization stable. Every gain lies in [-1, 1].

> **Implementation check:** with only three fixed-action experts and one uniform expert, feed a written opposing sequence through the update. Compute one update by hand and verify that all weights remain finite, nonnegative and normalized after conversion to probabilities.

The code needs only the standard library. Keep the pool small and the state explicit; 501 throws are not enough to identify dozens of nearly identical experts reliably.

**Reading:** Freund and Schapire, *A Decision-Theoretic Generalization of On-Line Learning and an Application to Boosting* (1997), DOI 10.1006/jcss.1997.1504. Arora, Hazan and Kale's 2012 survey develops the broader multiplicative-weights framework; its link is on the last page.
---page---
# State the guarantee you mean

For the undiscounted exponential update above, with K experts and gains in [-1,1], the usual potential argument gives a pathwise bound against the experts' gains on the **realized history**:

```text
max_i sum_t g_i,t - sum_t sum_i alpha_i,t * g_i,t
    <= log(K) / eta + eta * T / 2
```

Here alpha is the normalized weight. With `eta = sqrt(2*log(K)/T)`, the right side is `sqrt(2*T*log(K))`. The mixture's conditional expected gain equals the weighted virtual gain when the opponent cannot see your current random draw. Actual sampled gains still fluctuate.

## Experiment 2: what uniform contributes

A uniform expert has virtual gain exactly zero against every revealed opposing move. Including it makes the bound a useful comparison with the equilibrium baseline. For K=8 and T=501, the bound divided by T is about 0.091. This is a finite-horizon expectation statement for the sampled policy, not a promise of a nonnegative score in every match.

Derive the displayed bound yourself by comparing the final log sum of weights with the weight of one expert, and bounding each log moment-generating function for a variable in [-1,1]. Be explicit about where the range of the gain enters the constant.

## The counterfactual trap

Against an adaptive opponent, an expert's virtual gain is not the score it would necessarily have earned by controlling the **entire match**. Different past actions could have trained the opponent differently. The comparator uses proposals on the history that actually occurred, not a hypothetical alternative trajectory.

This distinction matters against Cycle Counter, Markov and Adaptive Ensemble. Record both the portfolio's result and separate fresh matches played by each expert alone. A discrepancy is not automatically a bug in the weighting rule.

> **Checkpoint:** write three distinct claims: the pathwise bound on virtual gains, the expectation statement for your sampled moves, and a high-probability statement you have *not* proved. Do not replace one with another when reporting results.

**Optional extension:** add discounting to react faster to regime changes. The standard undiscounted bound above no longer applies unchanged. Label the discounted version as a separate empirical experiment and compare it against Shifting Bias.
---page---
# Spend an exploitation budget

Suppose you want an explicit bound on how far a prediction-driven policy can move from the uniform baseline. Let u be uniform and r be any learned action distribution. Play:

```text
p = (1 - rho) * u + rho * r,       0 <= rho <= 1
```

For a non-anticipating opponent, uniform contributes zero conditional expected payoff and r contributes at least -1. Therefore p's conditional expected payoff is at least `-rho` on each throw. This bound is deliberately crude, but its assumptions and meaning are clear.

## Experiment 3: pay for confidence

Compare rho values 0, 0.25, 0.5 and 1 while holding the learned policy fixed. Against a genuinely predictable bot, a small rho gives up some available advantage. Against a model that is confidently wrong, it limits the expected loss relative to an unrestricted deterministic reply.

A confidence-triggered rho is a further experiment. You might use the sample count in the current context or a validation score from stored predictions. Neither turns a correlated, adapting opponent into independent data. Avoid advertising a confidence bound whose sampling assumptions the match violates.

| Variant | Stationary bias | Changing bias | Adaptive learner | Uniform |
| --- | --- | --- | --- | --- |
| Uniform |  |  |  |  |
| Portfolio |  |  |  |  |
| Portfolio mixed with uniform |  |  |  |  |
| Discounted portfolio |  |  |  |  |

Use a fresh group of seeds for this comparison. Keep model state separate from the sampling RNG and reset both in setup. If you log predictions, verify that scoring a proposal never changes the action it would have recommended before the observed move.

> **Challenge:** construct an opponent that changes behavior in response to your policy, then explain which parts of your evaluation remain valid and which would require a model of that response. Do not use hidden current moves, shared PRNG reconstruction or server side channels as the "prediction."

The tournament rewards winning fixed series against a mixed field. A low-regret per-throw policy is an interesting baseline, but the event's terminal objective creates another decision problem.
---page---
# Optimize the series, not just the mean

Suppose you know a stationary opposing distribution q. With one throw left and a one-point lead, you may prefer a reply that avoids losing to one with a larger expected net payoff but a larger loss probability. With a deficit, the preference can reverse.

## Experiment 4: a finite-horizon controller

Let `V(n,d)` be the best expected match points with n throws remaining and current score difference d. At the end:

```text
V(0,d) = 1 if d > 0;  0.5 if d == 0;  0 if d < 0
```

For a candidate move a, q determines probabilities W(a), D(a) and L(a) of a throw win, draw and loss. The backward recursion is:

```text
V(n,d) = max_a [ W(a)*V(n-1,d+1)
              + D(a)*V(n-1,d)
              + L(a)*V(n-1,d-1) ]
```

For a fixed known q, the maximum of this linear expression occurs at a pure action, except for ties. Mixed actions can still be useful once uncertainty and an adaptive opponent are part of the problem; those are additional assumptions, not features already represented by this recursion.

Start with only the final **30 throws**. Precompute a small table or memoize the state; do not recompute a full 501-throw dynamic program on every move. From histories, d is your number of wins minus losses, and the number of throws remaining includes the choice you are about to make.

## A hand-checkable example

Take q = 30% rock, 60% paper, 10% scissors. The net-payoff maximizer is scissors (+0.30); paper earns +0.20. With one throw left and d=0, scissors also has the largest expected terminal points: `0.60 + 0.5*0.10 = 0.65`. But with d=1:

- Paper loses with probability 0.10, so its expected match points are `1 - 0.5*0.10 = 0.95`.
- Scissors loses with probability 0.30, so its expected match points are 0.85.

Paper is now better for the match objective. Verify all three choices, then find what changes at d=-1. This is a calculation about the objective, not a conclusion from one anecdotal match.

> **Checkpoint:** test the terminal conditions and one-step recursion by hand. Then compare the controller with a per-throw best response against a fixed synthetic distribution before using estimated q from a real opponent.
---page---
# An experiment worth presenting

Choose one question you can answer within the session. A small, honest result is more informative than a large portfolio of untested claims.

## Three possible investigations

**Hidden order.** Compare context lengths one, two and three against Double Take, then add noise or a regime switch to your local test sequence. Measure the sample cost of discovering the longer dependency and the cost of retaining it after the regime changes.

**Adaptive opposition.** Compare an undiscounted portfolio, a discounted portfolio and its individual experts against Markov and Adaptive Ensemble. Explain the gap between one-step virtual gains and separate complete-match outcomes.

**Terminal utility.** Compare a final-30-throw controller with a net-payoff response. First use a known stationary q, then use an estimated q. Separate the effect of the objective from the effect of estimation error.

## Report enough to reproduce it

```bash
rps-cli play --against double_take,markov,adaptive_ensemble \
  --best-of 501 --games 10 --seed 2000 --output evaluation.json
rps-cli package --output reviewed-bot.zip
```

Keep the kit version, bot source, selected opponents, series length and seed range with the results. Use independent matches as your experimental units. Match outcomes and mean throw payoff should both be visible, and zero errors should be established before interpreting strategy quality.

Check numerical stability, empty contexts, repeated setup, tie-breaking and the timing of every prediction update. On a Raspberry Pi, a tiny standard-library model that returns promptly is more useful for this event than a large model whose startup or move computation times out.

> **Finish:** submit a tested version, confirm it is active, and give another participant a concise account of one assumption, one measured result and one limitation. Leave them enough detail to rerun the experiment.

## Further reading

- Arora, Hazan and Kale (2012), *The Multiplicative Weights Update Method: A Meta-Algorithm and Applications*. Theory of Computing 8, 121-164. https://theoryofcomputing.org/articles/v008a006/
- Freund and Schapire (1997), *A Decision-Theoretic Generalization of On-Line Learning and an Application to Boosting*. Journal of Computer and System Sciences 55, 119-139. https://doi.org/10.1006/jcss.1997.1504
- Yale Open Courses, ECON 159, Lecture 8, mixed strategies and rock-paper-scissors. https://oyc.yale.edu/economics/econ-159/lecture-8

The handout's RPS payoff calculations and finite-horizon experiments can be checked directly from the three-by-three payoff table. The online-learning references supply the broader framework; no claim here implies a reliable exploit of independent uniform random play.
