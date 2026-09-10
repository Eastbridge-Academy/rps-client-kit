"""Freeze estimated q for the final 30 throws; this is an experiment, not known q."""
from random import Random
from lesson_models import MOVES, TerminalController, best_response, frequencies, payoff

_rng = Random()
_controller = None


def setup(config):
    global _controller
    _rng.seed(config["seed"])
    _controller = None


def next_move(my_history, opponent_history, match_state):
    global _controller
    remaining = match_state["best_of"] - len(opponent_history)
    if remaining > 30:
        return _rng.choices(MOVES, weights=best_response(frequencies(opponent_history)))[0]
    if _controller is None:
        _controller = TerminalController(frequencies(opponent_history))
    difference = sum(payoff(a, b) for a, b in zip(my_history, opponent_history))
    return _controller.choose(remaining, difference)
