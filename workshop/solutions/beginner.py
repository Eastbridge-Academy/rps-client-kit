"""Eight-observation pattern checks; uniform fallback when predictions conflict."""
from random import Random
from rpsdk import Move

COUNTER = {Move.ROCK: Move.PAPER, Move.PAPER: Move.SCISSORS, Move.SCISSORS: Move.ROCK}
_rng = Random()


def setup(config):
    _rng.seed(config["seed"])


def next_move(my_history, opponent_history, match_state):
    n = len(opponent_history)
    predictions = set()
    if n >= 10:
        recent = range(n - 8, n)
        if len(set(opponent_history[-8:])) == 1:
            predictions.add(opponent_history[-1])
        if all(opponent_history[i] == COUNTER[opponent_history[i - 1]] for i in recent):
            predictions.add(COUNTER[opponent_history[-1]])
        if all(opponent_history[i] == my_history[i - 1] for i in recent):
            predictions.add(my_history[-1])
        if all(opponent_history[i] == my_history[i - 2] for i in recent):
            predictions.add(my_history[-2])
    if len(predictions) == 1:
        return COUNTER[predictions.pop()]
    return _rng.choice(list(Move))
