"""Balanced moves and adjacent pairs hide a deterministic nine-throw cycle."""

from random import Random
from rpsdk import Move

# A ternary de Bruijn cycle of order two. Each ordered pair appears once,
# including the wraparound pair; two previous throws identify the phase.
_cycle = [list(Move)[index] for index in (0, 0, 1, 0, 2, 1, 1, 2, 2)]
_phase = 0


def setup(config):
    global _phase
    _phase = Random(config["seed"]).randrange(len(_cycle))


def next_move(my_history, opponent_history, match_state):
    return _cycle[(_phase + match_state["round"]) % len(_cycle)]
