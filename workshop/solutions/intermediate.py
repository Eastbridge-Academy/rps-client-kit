"""A recent-window payoff response. Deliberately does not model dependencies."""
from random import Random
from lesson_models import MOVES, best_response, frequencies

_rng = Random()


def setup(config):
    _rng.seed(config["seed"])


def next_move(my_history, opponent_history, match_state):
    probabilities = best_response(frequencies(opponent_history[-30:]))
    return _rng.choices(MOVES, weights=probabilities)[0]
