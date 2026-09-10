"""Repeat the opponent's move from two throws ago."""

from random import Random
from rpsdk import Move

_rng = Random()


def setup(config):
    _rng.seed(config["seed"])


def next_move(my_history, opponent_history, match_state):
    return opponent_history[-2] if len(opponent_history) >= 2 else _rng.choice(list(Move))
