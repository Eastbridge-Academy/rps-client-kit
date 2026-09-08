"""Switch the favored throw every 50 rounds; punish slow frequency trackers."""

from random import Random
from rpsdk import Move

_rng = Random()
_phase = 0


def setup(config):
    global _phase
    _rng.seed(config["seed"])
    _phase = _rng.randrange(3)


def next_move(my_history, opponent_history, match_state):
    favorite = (match_state["round"] // 50 + _phase) % 3
    weights = [15, 15, 15]
    weights[favorite] = 70
    return _rng.choices(list(Move), weights=weights)[0]
