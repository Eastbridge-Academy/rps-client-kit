"""Match recent sequences of 2–5 opponent throws and predict their continuation."""

from collections import Counter
from random import Random
from rpsdk import Move

_rng = Random()
_counter = {Move.ROCK: Move.PAPER, Move.PAPER: Move.SCISSORS, Move.SCISSORS: Move.ROCK}


def setup(config):
    _rng.seed(config["seed"])


def next_move(my_history, opponent_history, match_state):
    history = opponent_history[-150:]
    for width in range(min(5, len(history) - 1), 1, -1):
        suffix = history[-width:]
        continuations = Counter(
            history[i + width]
            for i in range(len(history) - width)
            if history[i : i + width] == suffix
        )
        if continuations:
            largest = max(continuations.values())
            prediction = _rng.choice(
                [move for move in Move if continuations[move] == largest]
            )
            return _counter[prediction]
    return _rng.choice(list(Move))
