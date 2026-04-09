from rpsdk import Move

_moves = [Move.ROCK, Move.PAPER, Move.SCISSORS]
_index = 0


def next_move(my_history, opponent_history, match_state):
    global _index
    move = _moves[_index]
    _index = (_index + 1) % len(_moves)
    return move
