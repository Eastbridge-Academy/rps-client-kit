from __future__ import annotations

from typer.testing import CliRunner

from rps_client.cli import app

runner = CliRunner()


def test_init_command_creates_starter_bot(tmp_path):
    result = runner.invoke(app, ["init", str(tmp_path)])

    assert result.exit_code == 0
    assert (tmp_path / "bot.py").exists()
    assert "Starter bot written" in result.stdout


def test_validate_command_runs_local_check(tmp_path, monkeypatch):
    (tmp_path / "bot.py").write_text(
        """
from rps_client import rpsdk

def next_move(my_history, opponent_history, match_state):
    return rpsdk.Move.ROCK
"""
    )
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["validate", "--no-smoke"])

    assert result.exit_code == 0
    assert "Local validation passed." in result.stdout
