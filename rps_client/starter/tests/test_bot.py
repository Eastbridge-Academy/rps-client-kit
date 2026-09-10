"""Contract checks, not a test of how often your strategy wins."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

from rpsdk import Move


def load_bot():
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    spec = spec_from_file_location("workshop_bot", root / "bot.py")
    bot = module_from_spec(spec)
    spec.loader.exec_module(bot)
    if hasattr(bot, "setup"):
        bot.setup({"seed": 42})
    return bot


def test_first_throw_handles_empty_history():
    bot = load_bot()
    move = bot.next_move([], [], {"round": 0, "best_of": 501, "seed": 42,
                                "last_outcome": None, "timeouts": 0, "opponent_timeouts": 0})
    assert Move.from_value(move) in list(Move)


def test_bot_can_play_a_complete_series():
    bot = load_bot()
    mine, theirs = [], []
    last_outcome = None
    for turn in range(501):
        state = {"round": turn, "best_of": 501, "seed": 42,
                 "last_outcome": last_outcome, "timeouts": 0, "opponent_timeouts": 0}
        my_move = Move.from_value(bot.next_move(list(mine), list(theirs), state))
        opponent_move = list(Move)[turn % 3]
        mine.append(my_move)
        theirs.append(opponent_move)
        last_outcome = "draw" if my_move == opponent_move else "win" if my_move.beats(opponent_move) else "loss"
    assert len(mine) == 501
