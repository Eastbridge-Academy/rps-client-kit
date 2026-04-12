"""Helpers for loading and exercising participant bots locally."""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Callable

from rps_client.rpsdk import Move


class ParticipantBotError(RuntimeError):
    """Raised when a participant bot cannot be loaded or executed safely."""


@dataclass
class LoadedParticipantBot:
    module: ModuleType
    next_move: Callable[[list[Move], list[Move], dict], Move | str]
    setup: Callable[[dict], None] | None


def load_participant_bot(path: Path) -> LoadedParticipantBot:
    resolved_path = path.resolve()
    if not resolved_path.exists():
        raise ParticipantBotError(f"No bot.py found at {resolved_path}.")

    spec = importlib.util.spec_from_file_location("participant_bot", resolved_path)
    if spec is None or spec.loader is None:
        raise ParticipantBotError(f"Unable to load {resolved_path.name}.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[assignment]

    next_move = getattr(module, "next_move", None)
    if not callable(next_move):
        raise ParticipantBotError("bot.py must define a callable next_move(my_history, opponent_history, match_state).")

    setup = getattr(module, "setup", None)
    if setup is not None and not callable(setup):
        raise ParticipantBotError("setup(config) must be callable when defined.")

    return LoadedParticipantBot(module=module, next_move=next_move, setup=setup)


def build_sample_match_state(*, seed: int, round_number: int = 0, best_of: int = 9) -> dict:
    return {
        "round": round_number,
        "best_of": best_of,
        "seed": seed,
        "opponent_last_outcome": "draw",
        "timeouts": 0,
        "opponent_timeouts": 0,
    }
