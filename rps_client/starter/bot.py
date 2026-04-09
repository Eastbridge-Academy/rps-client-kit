"""Sample Rock-Paper-Scissors bot template."""

from __future__ import annotations

from random import Random
from typing import Dict, List

from rpsdk import Move  # provided by tournament environment

_rng = Random()


def setup(config: Dict) -> None:
    """Called once before the match starts."""
    seed = config.get("seed")
    if seed is not None:
        _rng.seed(seed)


def next_move(my_history: List[Move], opponent_history: List[Move], match_state: Dict) -> Move:
    """Return your next move.

    Default implementation: randomly choose among the three moves. Replace with your strategy!
    """
    return _rng.choice([Move.ROCK, Move.PAPER, Move.SCISSORS])
