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
    bot_file.write_text("print('hi')\n")
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

    assert captured["url"] == "http://example.com/api/v1/bots/submit"
    assert captured["headers"] == {"X-Submit-Token": "secret"}
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
        assert zf.read("bot.py").decode() == "print('hi')\n"

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
