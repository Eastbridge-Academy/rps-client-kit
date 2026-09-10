"""Shared house bot catalogue used by API scripts and local tooling."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from importlib import resources

_BOTS_PACKAGE = "rps_house_bots.bots"

# One catalogue feeds the CLI, event field guide and server seeding metadata.
_PROFILES = {
    "rocky": ("Beginner", "Always plays rock.", "Play paper. You should win every throw."),
    "cycle_rps": ("Beginner", "Plays rock, paper, scissors, then repeats.", "Work out the next move in the cycle and play the move that beats it."),
    "copycat": ("Beginner", "Copies your previous throw after a random opening.", "If you last played rock, it will play rock next. Use your own history to choose a reply."),
    "echo_two": ("Beginner", "Copies your throw from two turns ago.", "Use my_history[-2] once two throws have finished."),
    "contrarian": ("Intermediate", "Plays the move that beats your previous throw, after a random opening.", "If you last played rock, expect paper and reply with scissors."),
    "switcheroo": ("Intermediate", "Plays rock for the first half of the match and scissors afterwards.", "Compare counts over the last 30 throws with counts over the whole match."),
    "biased_random": ("Intermediate", "Independent throws: 60% rock, 25% paper, 15% scissors.", "Paper has expected net payoff +0.45 per throw."),
    "shifting_bias": ("Intermediate", "Changes its favorite move every 50 throws, choosing it 70% of the time.", "Try a recent window or discount old counts. How long does your bot take to notice a switch?"),
    "sticky": ("Intermediate", "Repeats its last move 80% of the time; each alternative has probability 10%.", "Counter its last move. Compare that with a bot that uses only total move counts."),
    "win_stay_lose_shift": ("Intermediate", "Repeats after a win or draw. After a loss, chooses either other move with equal probability.", "After it wins or draws, counter its last move. After it loses, play the move its last move beats."),
    "cycle_counter": ("Advanced", "Counters your most common move over the last ten throws.", "Model its sliding window, including the tie-break from the earliest tied occurrence."),
    "markov": ("Advanced", "Learns what follows your last move and counters that prediction.", "Reconstruct its counts from your own history, or balance what follows each of your moves."),
    "double_take": ("Advanced", "Repeats a nine-throw cycle. Each move and each adjacent pair appears equally often.", "Record what follows each pair of moves. Compare this with a table using only the last move."),
    "sequence_hunter": ("Expert", "Looks for earlier occurrences of your last 2-5 moves within your last 150 throws.", "Try a sequence where the same five-move ending has different successors. Which does it predict?"),
    "adaptive_ensemble": ("Expert", "Chooses among repeat, frequency, cycle and reactive predictors using their recent accuracy.", "Change your rule partway through a match and measure how long it takes to catch up."),
    "random_uniform": ("Baseline", "Chooses each move independently with equal probability, using a seeded generator.", "Use several seeds to see how much scores vary against random play."),
}


@dataclass(frozen=True)
class BotSpec:
    slug: str
    game_type: str = "rps"

    @property
    def level(self) -> str:
        return _PROFILES[self.slug][0]

    @property
    def description(self) -> str:
        return _PROFILES[self.slug][1]

    @property
    def hint(self) -> str:
        return _PROFILES[self.slug][2]

    @property
    def display_name(self) -> str:
        return self.slug.replace("_", " ").title()


def list_bots() -> list[BotSpec]:
    """Return all available house bot specifications."""
    bot_dir = resources.files(_BOTS_PACKAGE)
    specs: list[BotSpec] = []
    for entry in bot_dir.iterdir():
        if (
            entry.is_file()
            and entry.name.endswith(".py")
            and entry.name != "__init__.py"
        ):
            specs.append(BotSpec(slug=entry.name.removesuffix(".py")))
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


def get_bot_files(slug: str) -> dict[str, str]:
    """Package a house bot with the SDK version used by this catalogue."""
    return {
        "bot.py": get_bot_source(slug),
        "rpsdk/__init__.py": resources.files("rpsdk")
        .joinpath("__init__.py")
        .read_text(encoding="utf-8"),
    }
