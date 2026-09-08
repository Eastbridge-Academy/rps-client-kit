"""Track decaying accuracy of repeat, frequency, cycle and reactive predictors."""

from collections import Counter
from random import Random
from rpsdk import Move

_rng = Random()
_counter = {Move.ROCK: Move.PAPER, Move.PAPER: Move.SCISSORS, Move.SCISSORS: Move.ROCK}
_scores = [0.0] * 4
_predictions = []


def setup(config):
    global _scores, _predictions
    _rng.seed(config["seed"])
    _scores = [0.0] * 4
    _predictions = []


def next_move(my_history, opponent_history, match_state):
    global _scores, _predictions
    if not opponent_history:
        return _rng.choice(list(Move))
    if _predictions:
        observed = opponent_history[-1]
        _scores = [
            score * 0.96 + (prediction == observed)
            for score, prediction in zip(_scores, _predictions)
        ]
    frequent = Counter(opponent_history[-30:]).most_common(1)[0][0]
    _predictions = [
        opponent_history[-1],
        frequent,
        _counter[opponent_history[-1]],
        _counter[my_history[-1]],
    ]
    leaders = [i for i, score in enumerate(_scores) if score == max(_scores)]
    return _counter[_predictions[_rng.choice(leaders)]]
