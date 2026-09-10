"""Your tournament bot. Edit next_move, then test, practice and submit."""

from random import Random
from rpsdk import Move

_rng = Random()


def setup(config: dict) -> None:
    """Runs once per match. Reset any learned state here."""
    _rng.seed(config["seed"])


def next_move(my_history: list[Move], opponent_history: list[Move], match_state: dict) -> Move:
    """Both histories contain completed throws, oldest first.

    They are empty on the first call. opponent_history[-1] is the opponent's
    previous throw, never their current choice. A new match starts fresh.
    """
    # This baseline is legal and ready to submit. Try replacing it with a
    # prediction, then play the move that beats your prediction.
    return _rng.choice(list(Move))
