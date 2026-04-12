"""Local validation helpers for participant bots."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from rich.console import Console

from rps_client.participant_bot import ParticipantBotError, build_sample_match_state, load_participant_bot
from rps_client.rpsdk import Move
from rps_client.simulator import run_local_simulation

console = Console()

DEFAULT_VALIDATION_SEED = 4242
DEFAULT_SMOKE_OPPONENTS = ("rocky", "copycat")


def validate_local_bot(
    *,
    bot_path: Path,
    smoke_opponents: Iterable[str] | None = None,
    best_of: int = 9,
    smoke: bool = True,
) -> None:
    try:
        loaded_bot = load_participant_bot(bot_path)
    except ParticipantBotError as exc:
        console.print(f"[red]{exc}[/red]")
        raise SystemExit(1) from exc
    except Exception as exc:
        console.print(f"[red]Could not import {bot_path}: {exc}[/red]")
        raise SystemExit(1) from exc

    try:
        if loaded_bot.setup is not None:
            loaded_bot.setup({"seed": DEFAULT_VALIDATION_SEED})

        preview_move = Move.from_value(
            loaded_bot.next_move(
                [],
                [],
                build_sample_match_state(seed=DEFAULT_VALIDATION_SEED, best_of=best_of),
            )
        )
    except Exception as exc:
        console.print(f"[red]{_format_validation_failure(exc)}[/red]")
        raise SystemExit(1) from exc

    console.print("[green]Local validation passed.[/green]")
    console.print(f"Preview move: {preview_move.value}")

    if not smoke:
        return

    opponents = list(smoke_opponents or DEFAULT_SMOKE_OPPONENTS)
    console.print(f"Running smoke matches against: {', '.join(opponents)}")
    run_local_simulation(opponents, best_of=best_of, bot_path=bot_path)


def _format_validation_failure(exc: Exception) -> str:
    if isinstance(exc, ValueError):
        return (
            "next_move(...) must return one of rock, paper, or scissors. "
            f"Original error: {exc}"
        )
    return f"Local validation failed: {type(exc).__name__}: {exc}"
