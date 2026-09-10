from __future__ import annotations

import io
import zipfile

import httpx
import pytest

from rps_client.config import ConfigStore
from rps_client.submission import submit_bot_archive


class DummyResponse:
    def __init__(self, status_code: int = 202, payload: dict | None = None, text: str = "") -> None:
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self) -> dict:
        return self._payload


def test_submit_bot_archive_success(monkeypatch, tmp_path, capsys):
    bot_dir = tmp_path / "workspace"
    bot_dir.mkdir()
    bot_file = bot_dir / "bot.py"
    bot_file.write_text("import helpers\nprint('hi')\n")
    (bot_dir / "helpers.py").write_text("x = 1\n")
    data_dir = bot_dir / "data"
    data_dir.mkdir()
    (data_dir / "info.txt").write_text("ok\n")

    config = ConfigStore(path=tmp_path / "config.json")
    config.token = "secret"
    config.api_url = "http://example.com"

    captured: dict = {}

    def fake_post(url, *, headers, data, files, timeout):  # type: ignore[override]
        captured["url"] = url
        captured["headers"] = headers
        captured["data"] = data
        captured["files"] = files
        return DummyResponse(payload={"message": "Submission received and queued for validation."})

    monkeypatch.setattr(httpx, "post", fake_post)

    submit_bot_archive(team_name="Team", bot_path=bot_file, notes="hello", config=config)

    assert captured["url"] == "http://example.com/api/v1/leagues/rps/bots/submit"
    assert captured["headers"] == {"Authorization": "Bearer secret"}
    assert captured["data"]["team_name"] == "Team"
    assert captured["data"]["notes"] == "hello"

    filename, archive_bytes, content_type = captured["files"]["archive"]
    assert filename == "submission.zip"
    assert content_type == "application/zip"

    with zipfile.ZipFile(io.BytesIO(archive_bytes), "r") as zf:
        names = zf.namelist()
        assert "bot.py" in names
        assert "helpers.py" in names
        assert "data/info.txt" in names
        assert zf.read("bot.py").decode() == "import helpers\nprint('hi')\n"

    out = capsys.readouterr().out
    assert "queued for validation" in out
    assert 'rps-cli status "Team"' in out


def test_submit_bot_archive_requires_token(tmp_path):
    bot_file = tmp_path / "bot.py"
    bot_file.write_text("print('hi')\n")

    config = ConfigStore(path=tmp_path / "config.json")
    config.token = None

    with pytest.raises(SystemExit):
        submit_bot_archive(team_name="Team", bot_path=bot_file, notes=None, config=config)


def test_submit_bot_archive_handles_http_error(monkeypatch, tmp_path):
    bot_file = tmp_path / "bot.py"
    bot_file.write_text("print('hi')\n")

    config = ConfigStore(path=tmp_path / "config.json")
    config.token = "token"
    config.api_url = "http://example.com"

    def fake_post(*args, **kwargs):  # type: ignore[override]
        raise httpx.ConnectError("boom", request=None)

    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(SystemExit):
        submit_bot_archive(team_name="Team", bot_path=bot_file, notes=None, config=config)


def test_archive_includes_transitive_packages_but_not_config_tests_or_unrelated_scripts(tmp_path):
    from rps_client.submission import _build_submission_archive
    (tmp_path / "bot.py").write_text("from strategy.choose import move\ndef next_move(*args): return move()\n")
    package = tmp_path / "strategy"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "choose.py").write_text("from .values import MOVE\ndef move(): return MOVE\n")
    (package / "values.py").write_text("from rpsdk import Move\nMOVE = Move.PAPER\n")
    (tmp_path / "scratch.py").write_text("raise RuntimeError('not part of the bot')\n")
    (tmp_path / ".rps-cli.json").write_text('{"token": "private"}')
    archive = _build_submission_archive(tmp_path / "bot.py")
    with zipfile.ZipFile(io.BytesIO(archive)) as zf:
        assert set(zf.namelist()) == {"bot.py", "strategy/__init__.py", "strategy/choose.py", "strategy/values.py", "rpsdk/__init__.py"}
        assert b"private" not in b"".join(zf.read(name) for name in zf.namelist())
        target = tmp_path / "extracted"
        zf.extractall(target)
    from rps_client.validation import validate_local_bot
    validate_local_bot(bot_path=target / "bot.py", smoke=False)


def test_archive_rejects_data_symlinks_outside_project(tmp_path):
    from rps_client.submission import _build_submission_archive
    from rps_client.participant_bot import ParticipantBotError
    project = tmp_path / "bot"
    project.mkdir()
    (project / "bot.py").write_text("def next_move(*args): return 'rock'\n")
    (project / "data").mkdir()
    outside = tmp_path / "private.txt"
    outside.write_text("secret")
    (project / "data/leak.txt").symlink_to(outside)
    with pytest.raises(ParticipantBotError, match="symlink"):
        _build_submission_archive(project / "bot.py")
