from __future__ import annotations

from click import unstyle
from typer.testing import CliRunner

from rps_client.cli import app

runner = CliRunner()


def test_init_command_creates_starter_bot(tmp_path):
    result = runner.invoke(app, ["init", str(tmp_path)])

    assert result.exit_code == 0
    assert (tmp_path / "bot.py").exists()
    assert "Starter project ready" in result.stdout


def test_validate_command_runs_local_check(tmp_path, monkeypatch):
    (tmp_path / "bot.py").write_text(
        """
import rpsdk

def next_move(my_history, opponent_history, match_state):
    return rpsdk.Move.ROCK
"""
    )
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["validate", "--no-smoke"])

    assert result.exit_code == 0
    assert "Local validation passed." in result.stdout

def test_version_and_help_work_even_with_broken_project_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".rps-cli.json").write_text("broken")
    assert runner.invoke(app, ["--help"]).exit_code == 0
    version = runner.invoke(app, ["--version"])
    assert version.exit_code == 0
    assert "0.3.0" in version.stdout
    result = runner.invoke(app, ["info"])
    assert result.exit_code != 0
    # Rich may colour individual words and wrap the error panel on Windows.
    message = " ".join(unstyle(result.output).replace("│", " ").split())
    assert "valid JSON" in message
    assert "Traceback" not in result.output


def test_config_commands_are_project_local_and_mask_even_short_tokens(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert runner.invoke(app, ["config", "set", "token", "xyz"]).exit_code == 0
    assert (tmp_path / ".rps-cli.json").is_file()
    for args in (["info"], ["config", "get", "token"]):
        result = runner.invoke(app, args)
        assert result.exit_code == 0
        assert "xyz" not in result.stdout
        assert "configured" in result.stdout


def test_play_exports_seeded_complete_traces(tmp_path, monkeypatch):
    import json
    monkeypatch.chdir(tmp_path)
    (tmp_path / "bot.py").write_text("def next_move(*args): return 'paper'\n")
    result = runner.invoke(app, ["play", "--against", "rocky", "--best-of", "5",
                                 "--games", "2", "--seed", "100", "--output", "games.json"])
    assert result.exit_code == 0, result.output
    matches = json.loads((tmp_path / "games.json").read_text())["matches"]
    assert [item["seed"] for item in matches] == [100, 101]
    assert all(item["wins"] == 5 and len(item["rounds"]) == 5 for item in matches)


def test_opponent_catalogue_includes_hints():
    result = runner.invoke(app, ["opponents", "--hints"])
    assert result.exit_code == 0, result.output
    assert "double_take" in result.stdout
    assert "echo_two" in result.stdout


def test_doctor_checks_the_selected_active_rps_league(tmp_path, monkeypatch):
    import httpx
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("RPS_SUBMIT_TOKEN", "configured")
    monkeypatch.setenv("RPS_LEAGUE", "workshop")
    (tmp_path / "bot.py").write_text("def next_move(*args): return 'rock'\n")
    def get(url, **kwargs):
        data = [{"slug": "workshop", "name": "Workshop", "game_type": "rps", "is_active": True}] if url.endswith("/leagues") else {"status": "ok"}
        return httpx.Response(200, json=data, request=httpx.Request("GET", url))
    monkeypatch.setattr("rps_client.cli.httpx.get", get)
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0, result.output
    assert "Workshop is active" in result.output
    assert "validates the token when you submit" in result.output
    monkeypatch.setenv("RPS_LEAGUE", "wrong-slug")
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 1
    assert "Available: workshop" in result.output


def test_doctor_explains_untrusted_development_certificates(tmp_path, monkeypatch):
    import httpx
    monkeypatch.chdir(tmp_path)
    def get(*args, **kwargs):
        raise httpx.ConnectError("[SSL: CERTIFICATE_VERIFY_FAILED] unable to get local issuer")
    monkeypatch.setattr("rps_client.cli.httpx.get", get)
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 1
    assert "SSL_CERT_FILE" in result.output
    assert "Traceback" not in result.output
