"""Learn which throw follows each opponent throw, then counter the prediction."""

from collections import Counter
from random import Random
from rpsdk import Move

_rng = Random()
_counts = {}
_counter = {Move.ROCK: Move.PAPER, Move.PAPER: Move.SCISSORS, Move.SCISSORS: Move.ROCK}


def setup(config):
    global _counts
    _rng.seed(config["seed"])
    _counts = {move: Counter() for move in Move}


def next_move(my_history, opponent_history, match_state):
    if len(opponent_history) >= 2:
        _counts[opponent_history[-2]][opponent_history[-1]] += 1
    counts = _counts.get(opponent_history[-1]) if opponent_history else None
    if not counts:
        return _rng.choice(list(Move))
    largest = max(counts.values())
    predicted = _rng.choice([move for move in Move if counts[move] == largest])
    return _counter[predicted]
