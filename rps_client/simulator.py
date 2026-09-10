"""Reproducible local practice against the shared house bot catalogue."""

from __future__ import annotations

import multiprocessing
import random
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType

from rich.console import Console
from rich.table import Table

from rpsdk import Move
from rps_client.participant_bot import ParticipantBotError, load_participant_bot
from rps_house_bots import BotSpec, get_bot_source, list_bots

console = Console()
AVAILABLE_BOTS: dict[str, BotSpec] = {spec.slug: spec for spec in list_bots()}
DEFAULT_SEED = 42


@dataclass
class SimulationResult:
    opponent: str
    slug: str
    seed: int
    wins: int
    losses: int
    draws: int
    errors: int
    rounds: list[dict] = field(default_factory=list)


def run_local_simulation(
    opponent_names: Iterable[str] | None = None,
    *, best_of: int = 501, bot_path: Path = Path("bot.py"), seed: int = DEFAULT_SEED,
    games: int = 1, record: bool = False, timeout: float = 30,
) -> list[SimulationResult]:
    """Run every selected opponent/seed pair in a fresh process."""
    if not 1 <= best_of <= 10001 or not 1 <= games <= 100 or timeout <= 0:
        raise ValueError("Use 1-10001 throws, 1-100 games and a positive timeout.")
    opponents = list(AVAILABLE_BOTS) if opponent_names is None else list(dict.fromkeys(name.strip() for name in opponent_names))
    if not opponents or any(not name for name in opponents):
        raise ValueError("Select at least one opponent. Run rps-cli opponents for the catalogue.")
    unknown = [name for name in opponents if name not in AVAILABLE_BOTS]
    if unknown:
        raise ValueError(f"Unknown opponent '{', '.join(unknown)}'. Run rps-cli opponents for valid slugs.")
    if not bot_path.is_file():
        raise ParticipantBotError(f"No bot file at {bot_path}. Run rps-cli init in your bot folder.")
    table = Table(title=f"Local Simulation: {best_of} throws per match")
    for label in ("Opponent", "Seed", "Match", "Throws W-L-D", "Net / throw", "Errors"):
        table.add_column(label)
    results = []
    for slug in opponents:
        spec = AVAILABLE_BOTS[slug]
        for game in range(games):
            result = _run_fresh_match(bot_path.resolve(), spec, best_of, seed + game, record, timeout)
            results.append(result)
            table.add_row(f"{spec.display_name} ({slug})", str(result.seed), _summarise_outcome(result),
                          f"{result.wins}-{result.losses}-{result.draws}",
                          f"{(result.wins - result.losses) / best_of:+.3f}", str(result.errors))
    console.print(table)
    match_wins = sum(result.wins > result.losses for result in results)
    match_losses = sum(result.wins < result.losses for result in results)
    console.print(f"Matches: {match_wins} won, {match_losses} lost, {len(results) - match_wins - match_losses} drawn.")
    console.print("Practice scores are not Elo. Compare several fresh seeds before trusting an improvement.")
    return results


def _local_match_process(conn, bot_path: Path, spec: BotSpec, best_of: int, seed: int, record: bool) -> None:
    try:
        random.seed(seed)
        loaded = load_participant_bot(bot_path)
        if loaded.setup is not None:
            loaded.setup({"seed": seed})
        opponent = _load_house_bot(spec, seed=seed ^ 0x45D9F3B)
        conn.send(_simulate_series(loaded.next_move, opponent, best_of=best_of, seed=seed, record=record))
    except BaseException as exc:
        conn.send(f"{type(exc).__name__}: {exc}")
    finally:
        conn.close()


def _run_fresh_match(bot_path: Path, spec: BotSpec, best_of: int, seed: int,
                     record: bool, timeout: float) -> SimulationResult:
    # A fresh process resets helper modules, stdlib RNG and learned state. This
    # whole-match deadline is a convenience limit, not the arena's per-move limit.
    ctx = multiprocessing.get_context("spawn")
    parent, child = ctx.Pipe(duplex=False)
    process = ctx.Process(target=_local_match_process, args=(child, bot_path, spec, best_of, seed, record))
    process.start()
    child.close()
    try:
        if not parent.poll(timeout):
            raise ParticipantBotError(f"Practice against {spec.slug} exceeded {timeout:g}s. Check for loops; use --timeout to allow a longer match.")
        try:
            result = parent.recv()
        except EOFError as exc:
            raise ParticipantBotError("Bot process exited during practice.") from exc
        if isinstance(result, str):
            raise ParticipantBotError(result)
        return result
    finally:
        parent.close()
        process.join(timeout=.2)
        if process.is_alive():
            process.kill()
            process.join()
        process.close()


def _simulate_series(
    participant_move: Callable[[list[Move], list[Move], dict], Move],
    opponent_bot: LoadedHouseBot,
    *, best_of: int, seed: int, record: bool = False,
) -> SimulationResult:
    rng = random.Random(seed)
    my_history: list[Move] = []
    opp_history: list[Move] = []
    wins = losses = draws = errors = 0
    rounds = []
    for round_number in range(best_of):
        match_state = {"round": round_number, "best_of": best_of, "seed": seed,
                       "last_outcome": _last_outcome_label(my_history, opp_history),
                       "timeouts": 0, "opponent_timeouts": 0}
        error = None
        try:
            my_move = Move.from_value(participant_move(list(my_history), list(opp_history), match_state))
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            my_move = rng.choice(list(Move))
            errors += 1
        opponent_state = {"round": round_number, "best_of": best_of, "seed": opponent_bot.seed,
                          "last_outcome": _last_outcome_label(opp_history, my_history),
                          "timeouts": 0, "opponent_timeouts": 0}
        opp_move = opponent_bot.next_move(list(opp_history), list(my_history), opponent_state)
        my_history.append(my_move)
        opp_history.append(opp_move)
        outcome = _determine_outcome(my_move, opp_move)
        wins += outcome > 0
        losses += outcome < 0
        draws += outcome == 0
        if record:
            rounds.append({"round": round_number, "my_move": my_move.value,
                           "opponent_move": opp_move.value, "outcome": outcome, "error": error})
    return SimulationResult(opponent_bot.spec.display_name, opponent_bot.spec.slug, seed,
                            wins, losses, draws, errors, rounds)


def _last_outcome_label(mine: list[Move], theirs: list[Move]) -> str | None:
    if not mine:
        return None
    outcome = _determine_outcome(mine[-1], theirs[-1])
    return "win" if outcome > 0 else "loss" if outcome < 0 else "draw"


def _determine_outcome(my_move: Move, opp_move: Move) -> int:
    return 0 if my_move == opp_move else 1 if my_move.beats(opp_move) else -1


def _summarise_outcome(result: SimulationResult) -> str:
    return "Win" if result.wins > result.losses else "Loss" if result.losses > result.wins else "Draw"


@dataclass
class LoadedHouseBot:
    spec: BotSpec
    module: ModuleType
    seed: int

    def next_move(self, my_history: list[Move], opponent_history: list[Move], match_state: dict) -> Move:
        return Move.from_value(self.module.next_move(my_history, opponent_history, match_state))


def _load_house_bot(spec: BotSpec, *, seed: int) -> LoadedHouseBot:
    module = ModuleType(f"house_bot_{spec.slug}")
    exec(get_bot_source(spec.slug), module.__dict__)
    setup = getattr(module, "setup", None)
    if callable(setup):
        setup({"seed": seed})
    if not callable(getattr(module, "next_move", None)):
        raise RuntimeError(f"House bot {spec.slug} missing next_move implementation")
    return LoadedHouseBot(spec=spec, module=module, seed=seed)
