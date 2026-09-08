"""An exploitable random baseline: rock 60%, paper 25%, scissors 15%."""

from random import Random
from rpsdk import Move

_rng = Random()


def setup(config):
    _rng.seed(config["seed"])


def next_move(my_history, opponent_history, match_state):
    return _rng.choices(list(Move), weights=[60, 25, 15])[0]
