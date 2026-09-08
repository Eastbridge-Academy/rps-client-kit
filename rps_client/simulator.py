"""Local simulation against built-in house bots."""

from __future__ import annotations

import multiprocessing
import random
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from rich.console import Console
from rich.table import Table

import rpsdk
from rps_client.participant_bot import ParticipantBotError, load_participant_bot
from rps_house_bots import BotSpec, get_bot_source, list_bots

console = Console()


Move = rpsdk.Move

AVAILABLE_BOTS: dict[str, BotSpec] = {spec.slug: spec for spec in list_bots()}
DEFAULT_SEED = 42


@dataclass
class SimulationResult:
    opponent: str
    wins: int
    losses: int
    draws: int
    errors: int


def run_local_simulation(
    opponent_names: Iterable[str] | None = None,
    *,
    best_of: int = 101,
    bot_path: Path = Path("bot.py"),
) -> list[SimulationResult]:
    """Execute fresh, initialized participant instances for every opponent."""
    if best_of <= 0:
        raise ValueError("Series length must be positive")
    results: list[SimulationResult] = []

    opponents = list(opponent_names or AVAILABLE_BOTS.keys())
    if not opponents:
        console.print("[yellow]No opponents selected.")
        return results

    table = Table(title="Local Simulation", show_lines=False)
    table.add_column("Opponent", style="cyan", justify="left")
    table.add_column("Outcome", style="green", justify="center")
    table.add_column("Record", style="white")
    table.add_column("Errors", style="red", justify="right")

    for slug in opponents:
        spec = AVAILABLE_BOTS.get(slug)
        if spec is None:
            console.print(f"[yellow]Unknown opponent '{slug}'. Skipping.")
            continue
        result = _run_fresh_match(bot_path.resolve(), spec, best_of)
        results.append(result)
        outcome = _summarise_outcome(result)
        label = f"{spec.display_name} ({spec.slug})"
        table.add_row(
            label,
            outcome,
            f"{result.wins}-{result.losses}-{result.draws}",
            str(result.errors),
        )

    console.print(table)
    return results


def _local_match_process(conn, bot_path: Path, spec: BotSpec, best_of: int) -> None:
    try:
        loaded = load_participant_bot(bot_path)
        if loaded.setup is not None:
            loaded.setup({"seed": DEFAULT_SEED})
        opponent = _load_house_bot(spec, seed=DEFAULT_SEED ^ 0x45D9F3B)
        conn.send(
            _simulate_series(
                loaded.next_move, opponent, best_of=best_of, seed=DEFAULT_SEED
            )
        )
    except BaseException as exc:
        conn.send(f"{type(exc).__name__}: {exc}")
    finally:
        conn.close()


def _run_fresh_match(bot_path: Path, spec: BotSpec, best_of: int) -> SimulationResult:
    # Spawn also resets helper-module globals and stdlib random state, which
    # reloading only bot.py does not. This remains a local practice tool; use
    # the arena engine for per-move time-limit and fallback acceptance checks.
    ctx = multiprocessing.get_context("spawn")
    parent, child = ctx.Pipe(duplex=False)
    process = ctx.Process(
        target=_local_match_process, args=(child, bot_path, spec, best_of)
    )
    process.start()
    child.close()
    try:
        if not parent.poll(12 + best_of * 2):
            raise ParticipantBotError(
                f"Practice match against {spec.slug} exceeded its time budget"
            )
        try:
            result = parent.recv()
        except EOFError as exc:
            raise ParticipantBotError("Bot process exited during practice") from exc
        if isinstance(result, str):
            raise ParticipantBotError(result)
        return result
    finally:
        parent.close()
        process.join(timeout=1)
        if process.is_alive():
            process.kill()
            process.join()
        process.close()


def _simulate_series(
    participant_move: Callable[[list[Move], list[Move], dict], Move],
    opponent_bot: LoadedHouseBot,
    *,
    best_of: int,
    seed: int,
) -> SimulationResult:
    rng = random.Random(seed)
    my_history: list[Move] = []
    opp_history: list[Move] = []
    wins = losses = draws = 0
    errors = 0

    for round_number in range(best_of):
        match_state = {
            "round": round_number,
            "best_of": best_of,
            "seed": seed,
            "opponent_last_outcome": _last_outcome_label(wins, losses),
            "timeouts": 0,
            "opponent_timeouts": 0,
        }

        try:
            my_move = Move.from_value(
                participant_move(list(my_history), list(opp_history), match_state)
            )
        except Exception as exc:  # pragma: no cover - defensive
            console.print(
                f"[red]Exception from bot in round {round_number} vs {opponent_bot.spec.slug}: {exc}"
            )
            my_move = rng.choice(list(Move))
            errors += 1

        opponent_state = {
            "round": round_number,
            "best_of": best_of,
            "seed": opponent_bot.seed,
            "opponent_last_outcome": _last_outcome_label(losses, wins),
            "timeouts": 0,
            "opponent_timeouts": 0,
        }
        opp_move = opponent_bot.next_move(
            list(opp_history), list(my_history), opponent_state
        )

        my_history.append(my_move)
        opp_history.append(opp_move)

        outcome = _determine_outcome(my_move, opp_move)
        if outcome > 0:
            wins += 1
        elif outcome < 0:
            losses += 1
        else:
            draws += 1

    return SimulationResult(
        opponent=opponent_bot.spec.display_name,
        wins=wins,
        losses=losses,
        draws=draws,
        errors=errors,
    )


def _last_outcome_label(wins: int, losses: int) -> str:
    if wins > losses:
        return "win"
    if losses > wins:
        return "loss"
    return "draw"


def _determine_outcome(my_move: Move, opp_move: Move) -> int:
    if my_move == opp_move:
        return 0
    if my_move.beats(opp_move):
        return 1
    return -1


def _summarise_outcome(result: SimulationResult) -> str:
    if result.wins > result.losses:
        return "Win"
    if result.losses > result.wins:
        return "Loss"
    return "Draw"


@dataclass
class LoadedHouseBot:
    spec: BotSpec
    module: ModuleType
    seed: int

    def next_move(
        self,
        my_history: list[Move],
        opponent_history: list[Move],
        match_state: dict,
    ) -> Move:
        move_callable = getattr(self.module, "next_move", None)
        if not callable(move_callable):
            raise RuntimeError(f"House bot {self.spec.slug} missing next_move")
        return Move.from_value(move_callable(my_history, opponent_history, match_state))


def _load_house_bot(spec: BotSpec, *, seed: int) -> LoadedHouseBot:
    module = ModuleType(f"house_bot_{spec.slug}")
    exec(get_bot_source(spec.slug), module.__dict__)

    setup_callable = module.__dict__.get("setup")
    if callable(setup_callable):
        setup_callable({"seed": seed})

    if "next_move" not in module.__dict__:
        raise RuntimeError(f"House bot {spec.slug} missing next_move implementation")

    return LoadedHouseBot(spec=spec, module=module, seed=seed)
