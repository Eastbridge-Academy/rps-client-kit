from random import Random

from rpsdk import Move

_rng = Random()

_counter = {
    Move.ROCK: Move.PAPER,
    Move.PAPER: Move.SCISSORS,
    Move.SCISSORS: Move.ROCK,
}


def next_move(my_history, opponent_history, match_state):
    if match_state.get("round") == 0:
        seed = match_state.get("seed")
        if seed is not None:
            _rng.seed(seed)
    if not opponent_history:
        return _rng.choice([Move.ROCK, Move.PAPER, Move.SCISSORS])
    return _counter[opponent_history[-1]]
