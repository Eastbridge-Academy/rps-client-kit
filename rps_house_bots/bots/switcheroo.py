from rpsdk import Move


def next_move(my_history, opponent_history, match_state):
    best_of = match_state.get("best_of", 501)
    halfway = best_of // 2
    if match_state.get("round", 0) < halfway:
        return Move.ROCK
    return Move.SCISSORS
