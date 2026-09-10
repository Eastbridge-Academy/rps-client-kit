"""Project-local participant configuration, with environment overrides."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

DEFAULT_API_URL = "https://arena.eastbrid.ge"
DEFAULT_LEAGUE = "rps"


class ConfigStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path if path is not None else Path.cwd() / ".rps-cli.json"
        self._values = {"api_url": DEFAULT_API_URL, "league": DEFAULT_LEAGUE, "token": None}
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                raise ValueError(f"Cannot read {self.path.name}. Check that it contains valid JSON.") from exc
            if not isinstance(data, dict):
                raise ValueError(f"{self.path.name} must contain a JSON object.")
            for key in self._values:
                if key in data:
                    self.set(key, data[key])

    def set(self, key: str, value: str | None) -> None:
        if key not in self._values:
            raise ValueError("Choose api_url, league, or token.")
        if value is not None and not isinstance(value, str):
            raise ValueError(f"{key} must be text.")
        value = value.strip() if isinstance(value, str) else value
        if key == "api_url":
            parsed = urlsplit(value or "")
            if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.query or parsed.fragment:
                raise ValueError("api_url must be a complete http:// or https:// server URL.")
            value = value.rstrip("/")
        elif key == "league" and not re.fullmatch(r"[a-z0-9]+(?:[-_][a-z0-9]+)*", value or ""):
            raise ValueError("league must be a slug such as rps or rps-rehearsal.")
        self._values[key] = value

    @property
    def token(self) -> str | None:
        return os.environ.get("RPS_SUBMIT_TOKEN", self._values["token"])

    @token.setter
    def token(self, value: str | None) -> None:
        self.set("token", value)

    @property
    def api_url(self) -> str:
        return os.environ.get("RPS_API_URL", self._values["api_url"]).rstrip("/")

    @api_url.setter
    def api_url(self, value: str) -> None:
        self.set("api_url", value)

    @property
    def league(self) -> str:
        return os.environ.get("RPS_LEAGUE", self._values["league"])

    @league.setter
    def league(self, value: str) -> None:
        self.set("league", value)

    def save(self) -> None:
        # Environment overrides affect commands, but are never copied into the
        # project file just because an unrelated setting was changed.
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            os.chmod(self.path, 0o600)
            handle.write(json.dumps(self._values, indent=2) + "\n")
