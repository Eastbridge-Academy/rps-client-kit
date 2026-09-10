"""Repeat the previous move with probability 0.8; otherwise switch."""

from random import Random
from rpsdk import Move

_rng = Random()


def setup(config):
    _rng.seed(config["seed"])


def next_move(my_history, opponent_history, match_state):
    if not my_history:
        return _rng.choice(list(Move))
    if _rng.random() < .8:
        return my_history[-1]
    return _rng.choice([move for move in Move if move != my_history[-1]])
