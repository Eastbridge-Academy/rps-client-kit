from collections import Counter

from rpsdk import Move

def next_move(my_history, opponent_history, match_state):
    if not opponent_history:
        return Move.ROCK
    counts = Counter(opponent_history[-10:])
    if not counts:
        return Move.ROCK
    most_common = counts.most_common(1)[0][0]
    if most_common == Move.ROCK:
        return Move.PAPER
    if most_common == Move.PAPER:
        return Move.SCISSORS
    return Move.ROCK
