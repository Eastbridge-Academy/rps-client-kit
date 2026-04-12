from __future__ import annotations

from pathlib import Path

import pytest

from rps_client.validation import validate_local_bot


def test_validate_local_bot_runs_smoke_matches(tmp_path, monkeypatch, capsys):
    bot_file = tmp_path / "bot.py"
    bot_file.write_text(
        """
from rps_client import rpsdk

def next_move(my_history, opponent_history, match_state):
    return rpsdk.Move.ROCK
"""
    )

    monkeypatch.chdir(tmp_path)

    validate_local_bot(bot_path=bot_file, smoke_opponents=["rocky"], best_of=5)

    out = capsys.readouterr().out
    assert "Local validation passed." in out
    assert "Running smoke matches against: rocky" in out
    assert "Local Simulation" in out


def test_validate_local_bot_reports_bad_return_value(tmp_path, capsys):
    bot_file = tmp_path / "bot.py"
    bot_file.write_text(
        """
def next_move(my_history, opponent_history, match_state):
    return "lizard"
"""
    )

    with pytest.raises(SystemExit):
        validate_local_bot(bot_path=bot_file, smoke=False)

    out = capsys.readouterr().out
    assert "must return one of rock, paper, or scissors" in out


def test_validate_local_bot_requires_callable_next_move(tmp_path, capsys):
    bot_file = tmp_path / "bot.py"
    bot_file.write_text("next_move = 'rock'\n")

    with pytest.raises(SystemExit):
        validate_local_bot(bot_path=bot_file, smoke=False)

    out = capsys.readouterr().out
    assert "callable next_move" in out
