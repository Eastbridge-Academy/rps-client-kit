"""Shared house bot catalogue used by API scripts and local tooling."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import resources
from typing import Iterable

_BOTS_PACKAGE = "rps_house_bots.bots"


@dataclass(frozen=True)
class BotSpec:
    slug: str

    @property
    def display_name(self) -> str:
        return self.slug.replace("_", " ").title()


def list_bots() -> list[BotSpec]:
    """Return all available house bot specifications."""
    bot_dir = resources.files(_BOTS_PACKAGE)
    specs: list[BotSpec] = []
    for entry in bot_dir.iterdir():
        if entry.suffix == ".py" and entry.name != "__init__.py":
            specs.append(BotSpec(slug=entry.stem))
    specs.sort(key=lambda spec: spec.slug)
    return specs


def get_bot_source(slug: str) -> str:
    """Return the raw Python source for the given bot."""
    path = resources.files(_BOTS_PACKAGE) / f"{slug}.py"
    if not path.is_file():
        raise KeyError(f"Unknown house bot '{slug}'")
    return path.read_text(encoding="utf-8")


def iter_bot_sources() -> Iterable[tuple[BotSpec, str]]:
    """Yield (spec, source) pairs for all house bots."""
    for spec in list_bots():
        yield spec, get_bot_source(spec.slug)
