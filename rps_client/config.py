"""Local configuration store for CLI."""

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Optional

import json

DEFAULT_API_URL = "http://127.0.0.1:8321"

@dataclass
class ConfigStore:
    path: Path = field(default_factory=lambda: Path.home() / ".rps-cli.json")
    token: Optional[str] = None
    api_url: str = DEFAULT_API_URL

    def __post_init__(self) -> None:
        if self.path.exists():
            self._load()
        self.token = os.environ.get("RPS_SUBMIT_TOKEN", self.token)
        self.api_url = os.environ.get("RPS_API_URL", self.api_url)

    def _load(self) -> None:
        data = json.loads(self.path.read_text())
        self.token = data.get("token")
        self.api_url = data.get("api_url", DEFAULT_API_URL)

    def save(self) -> None:
        payload = {"token": self.token, "api_url": self.api_url}
        self.path.write_text(json.dumps(payload, indent=2))
