from random import Random

from rpsdk import Move

_rng = Random()

_ALL_MOVES = [Move.ROCK, Move.PAPER, Move.SCISSORS]


def next_move(my_history, opponent_history, match_state):
    if match_state.get("round") == 0:
        seed = match_state.get("seed")
        if seed is not None:
            _rng.seed(seed)
    if not my_history:
        return _rng.choice(_ALL_MOVES)
    my_last = my_history[-1]
    opp_last = opponent_history[-1]
    # Win or draw: repeat last move
    if my_last.beats(opp_last) or my_last == opp_last:
        return my_last
    # Loss: switch to a random different move
    return _rng.choice([m for m in _ALL_MOVES if m != my_last])
