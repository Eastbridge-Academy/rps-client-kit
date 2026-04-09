import random

from rpsdk import Move

_rng = random.Random()


def next_move(my_history, opponent_history, match_state):
    seed = match_state.get("seed")
    if match_state.get("round") == 0 and seed is not None:
        _rng.seed(seed)
    return _rng.choice([Move.ROCK, Move.PAPER, Move.SCISSORS])
