"""Incremental order-two counts, backing off to order one and frequencies."""
from random import Random
from lesson_models import ContextCounts, MOVES, best_response

_rng = Random()
_model = ContextCounts(2)


def setup(config):
    global _model
    _rng.seed(config["seed"])
    _model = ContextCounts(2)


def next_move(my_history, opponent_history, match_state):
    _model.observe(opponent_history)
    probabilities = best_response(_model.predict(opponent_history))
    return _rng.choices(MOVES, weights=probabilities)[0]
