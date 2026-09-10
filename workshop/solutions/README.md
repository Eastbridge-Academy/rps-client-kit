# Facilitator reference implementations

These bots implement the workshop exercises. Each can replace bot.py in a
participant project. You can share them for comparison after participants have
tried the exercises, or let people start by reading and modifying one.

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
  conflicting predictions fall back to uniform. Short coincidences can still
  fool it. The handout builds up to this from individual opponent rules.
- Intermediate: a 30-throw window and maximum expected payoff, randomizing ties.
  It forgets old regimes but does not condition on sequence context.
- Advanced: update order-two counts incrementally, use Laplace smoothing, and
  back off when a context has fewer than three observations. Compare against
  order one on Double Take.
- Expert: eight action-distribution experts, stored proposals, undiscounted
  exponential weighting, stable normalization. Virtual scores use the history
  produced by the portfolio; an expert playing alone may face different responses.
- Terminal: frequency response until the last 30 throws, then dynamic programming
  with a fixed estimate of the opponent's distribution. It assumes that estimate
  holds for the rest of the match, so try it against a changing opponent too.

The full source checkout's `uv run pytest tests/test_workshop.py` checks the
mathematical examples, update timing, lesson snippets, and legal 501-throw play.
