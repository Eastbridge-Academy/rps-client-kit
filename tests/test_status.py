import httpx
import pytest

from rps_client.config import ConfigStore
from rps_client.status import show_bot_status


class DummyResponse:
    def __init__(self, *, status_code: int = 200, payload: dict | list | None = None) -> None:
        self.status_code = status_code
        self._payload = payload if payload is not None else {}

    def json(self):
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("boom", request=None, response=None)


def test_show_bot_status_displays_active_and_latest_versions(monkeypatch, tmp_path, capsys):
    config = ConfigStore(path=tmp_path / "config.json")
    config.api_url = "http://example.com"

    responses = iter(
        [
            DummyResponse(payload=[{"id": 7, "team_name": "Team Rocket"}]),
            DummyResponse(
                payload={
                    "bot_id": 7,
                    "team_name": "Team Rocket",
                    "operator_status": "active",
                    "active_version": {"id": 5, "version": 2, "status": "active", "created_at": "2026-04-10T00:00:00Z", "rejection_reason": None},
                    "latest_version": {"id": 6, "version": 3, "status": "rejected", "created_at": "2026-04-10T00:01:00Z", "rejection_reason": "Import failed"},
                }
            ),
        ]
    )
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: next(responses))

    show_bot_status(team_name="Team Rocket", config=config)

    out = capsys.readouterr().out
    assert "Team Rocket" in out
    assert "Operator status: active" in out
    assert "Active version: v2 (active)" in out
    assert "Latest version: v3 (rejected)" in out
    assert "Rejection reason: Import failed" in out
    assert "rerun `rps-cli validate`" in out
    assert "submit again" in out


def test_show_bot_status_explains_uploaded_state(monkeypatch, tmp_path, capsys):
    config = ConfigStore(path=tmp_path / "config.json")
    config.api_url = "http://example.com"

    responses = iter(
        [
            DummyResponse(payload=[{"id": 3, "team_name": "Queued Team"}]),
            DummyResponse(
                payload={
                    "bot_id": 3,
                    "team_name": "Queued Team",
                    "operator_status": "active",
                    "active_version": None,
                    "latest_version": {"id": 9, "version": 1, "status": "uploaded", "created_at": "2026-04-10T00:01:00Z", "rejection_reason": None},
                }
            ),
        ]
    )
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: next(responses))

    show_bot_status(team_name="Queued Team", config=config)

    out = capsys.readouterr().out
    assert "Latest version: v1 (uploaded)" in out
    assert "waiting for the validation worker" in out


def test_show_bot_status_errors_when_team_missing(monkeypatch, tmp_path):
    config = ConfigStore(path=tmp_path / "config.json")
    config.api_url = "http://example.com"
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: DummyResponse(payload=[]))

    with pytest.raises(SystemExit):
        show_bot_status(team_name="Unknown Team", config=config)
