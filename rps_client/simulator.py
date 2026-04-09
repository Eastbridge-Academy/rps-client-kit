"""Local simulation against built-in house bots."""

from __future__ import annotations

import importlib.util
import random
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Callable, Iterable, Optional

from rich.console import Console
from rich.table import Table

from rps_client import rpsdk
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


def run_local_simulation(opponent_names: Optional[Iterable[str]] = None, *, best_of: int = 101) -> None:
    """Execute local matches against built-in opponents and display results."""
    try:
        participant = _load_participant_bot(Path("bot.py"))
    except Exception as exc:  # pragma: no cover - CLI surface
        console.print(f"[red]Failed to load bot.py: {exc}")
        return

    opponents = list(opponent_names or AVAILABLE_BOTS.keys())
    if not opponents:
        console.print("[yellow]No opponents selected.")
        return

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
        opponent_bot = _load_house_bot(spec, seed=DEFAULT_SEED)
        result = _simulate_series(participant, opponent_bot, best_of=best_of, seed=DEFAULT_SEED)
        outcome = _summarise_outcome(result)
        label = f"{spec.display_name} ({spec.slug})"
        table.add_row(
            label,
            outcome,
            f"{result.wins}-{result.losses}-{result.draws}",
            str(result.errors),
        )

    console.print(table)


def _load_participant_bot(path: Path) -> Callable[[list[Move], list[Move], dict], Move]:
    if not path.exists():
        raise FileNotFoundError("No bot.py found in current directory")

    spec = importlib.util.spec_from_file_location("participant_bot", path)
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load bot.py")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[assignment]

    if not hasattr(module, "next_move"):
        raise AttributeError("bot.py must define a next_move function")
    next_move = getattr(module, "next_move")
    if not callable(next_move):
        raise TypeError("next_move must be callable")
    return next_move


def _simulate_series(
    participant_move: Callable[[list[Move], list[Move], dict], Move],
    opponent_bot: "LoadedHouseBot",
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
            my_move = Move.from_value(participant_move(list(my_history), list(opp_history), match_state))
        except Exception as exc:  # pragma: no cover - defensive
            console.print(
                f"[red]Exception from bot in round {round_number} vs {opponent_bot.spec.slug}: {exc}"
            )
            my_move = rng.choice(list(Move))
            errors += 1

        opp_move = opponent_bot.next_move(list(opp_history), list(my_history), match_state)

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
