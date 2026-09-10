"""Bounded local contract validation followed by optional smoke matches."""

from __future__ import annotations

import multiprocessing
import random
from collections.abc import Iterable
from pathlib import Path

from rich.console import Console

from rps_client.participant_bot import ParticipantBotError, build_sample_match_state, load_participant_bot
from rps_client.simulator import _last_outcome_label, run_local_simulation
from rpsdk import Move

console = Console()
DEFAULT_VALIDATION_SEED = 4242
DEFAULT_SMOKE_OPPONENTS = ("rocky", "copycat")


def _check_process(conn, bot_path: Path) -> None:
    try:
        random.seed(DEFAULT_VALIDATION_SEED)
        loaded = load_participant_bot(bot_path)
        if loaded.setup is not None:
            loaded.setup({"seed": DEFAULT_VALIDATION_SEED})
        mine, theirs = [], []
        for turn, opponent in enumerate(Move):
            state = build_sample_match_state(seed=DEFAULT_VALIDATION_SEED, round_number=turn, best_of=3)
            state["last_outcome"] = _last_outcome_label(mine, theirs)
            returned = loaded.next_move(list(mine), list(theirs), state)
            try:
                move = Move.from_value(returned)
            except (ValueError, AttributeError, TypeError) as exc:
                raise ParticipantBotError(f"next_move(...) must return one of rock, paper, or scissors. Original error: {exc}") from exc
            mine.append(move)
            theirs.append(opponent)
        conn.send((True, mine[0].value))
    except ParticipantBotError as exc:
        conn.send((False, str(exc)))
    except BaseException as exc:
        conn.send((False, _format_validation_failure(exc)))
    finally:
        conn.close()


def _check_contract(bot_path: Path, timeout: float = 10) -> str:
    ctx = multiprocessing.get_context("spawn")
    parent, child = ctx.Pipe(duplex=False)
    process = ctx.Process(target=_check_process, args=(child, bot_path.resolve()))
    process.start()
    child.close()
    try:
        if not parent.poll(timeout):
            raise ParticipantBotError("Local validation timed out. Check for loops or slow import, setup and next_move code.")
        try:
            success, message = parent.recv()
        except EOFError as exc:
            raise ParticipantBotError("Bot process exited during validation.") from exc
        if not success:
            raise ParticipantBotError(message)
        return message
    finally:
        parent.close()
        process.join(timeout=.2)
        if process.is_alive():
            process.kill()
            process.join()
        process.close()


def validate_local_bot(*, bot_path: Path, smoke_opponents: Iterable[str] | None = None,
                       best_of: int = 9, smoke: bool = True) -> None:
    try:
        preview = _check_contract(bot_path)
    except ParticipantBotError as exc:
        console.print(str(exc), style="red", markup=False)
        raise SystemExit(1) from exc
    console.print("[green]Local validation passed.[/green]")
    console.print(f"Preview move: {preview}")
    if smoke:
        opponents = list(DEFAULT_SMOKE_OPPONENTS) if smoke_opponents is None else list(smoke_opponents)
        console.print(f"Running smoke matches against: {', '.join(opponents)}")
        results = run_local_simulation(opponents, best_of=best_of, bot_path=bot_path)
        if any(result.errors for result in results):
            console.print("[red]Smoke matches found bot errors. Fix them before submitting.[/red]")
            raise SystemExit(1)


def _format_validation_failure(exc: BaseException) -> str:
    return f"Local validation failed: {type(exc).__name__}: {exc}"
