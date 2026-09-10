"""Undiscounted full-information portfolio from the expert route."""
from random import Random
from lesson_models import MOVES, Portfolio

_rng = Random()
_portfolio = None


def setup(config):
    global _portfolio
    _rng.seed(config["seed"])
    _portfolio = None


def next_move(my_history, opponent_history, match_state):
    global _portfolio
    if _portfolio is None:
        _portfolio = Portfolio(match_state["best_of"])
    probabilities = _portfolio.probabilities(my_history, opponent_history)
    return _rng.choices(MOVES, weights=probabilities)[0]
