# Facilitator reference implementations

These are small examples to inspect and modify, not guaranteed tournament winners.
Keep this directory off the starting student desktop if you prefer participants
to discover the ideas themselves. Each bot is a complete alternative to bot.py.

From this directory, after activating the participant environment:

```bash
rps-cli play --bot beginner.py --against rocky,cycle_rps,copycat,echo_two
rps-cli play --bot intermediate.py --against biased_random,shifting_bias
rps-cli play --bot advanced.py --against sticky,double_take
rps-cli play --bot expert.py --against markov,adaptive_ensemble
rps-cli play --bot terminal.py --against biased_random
rps-cli package --bot advanced.py --output advanced.zip
```

The packager follows the imported lesson_models package. To work in a separate
project, copy the selected file as bot.py **and** copy lesson_models beside it.
The beginner example is self-contained. Keep the starter tests in the project.

- Beginner: require eight matching recent transitions after ten observations;
  conflicting predictions fall back to uniform. It can mistake a short coincidence
  for a rule. The lesson starts with simpler named-opponent experiments.
- Intermediate: a 30-throw window and maximum expected payoff, randomizing ties.
  It forgets old regimes but does not condition on sequence context.
- Advanced: incremental order-two counts, Laplace smoothing and support-three
  backoff. Compare against order one to expose Double Take's hidden dependency.
- Expert: eight action-distribution experts, stored proposals, undiscounted
  exponential weighting, stable normalization. Virtual scores use the actual
  realized history, not counterfactual complete matches.
- Terminal: frequency response until the last 30 throws, then a fixed estimated-q
  dynamic program. Freezing an estimate makes the controller small and coherent;
  it does not make that estimate correct or model an adaptive opponent.

The full source checkout's `uv run pytest tests/test_workshop.py` checks the
mathematical examples, update timing, lesson snippets, and legal 501-throw play.
