"""Shared house bot catalogue used by API scripts and local tooling."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from importlib import resources

_BOTS_PACKAGE = "rps_house_bots.bots"

# One catalogue feeds the CLI, event field guide and server seeding metadata.
_PROFILES = {
    "rocky": ("Beginner", "Always rock.", "Play paper; check that it wins every throw."),
    "cycle_rps": ("Beginner", "Rock, paper, scissors, then repeat.", "Predict the next item in the cycle, not the last one."),
    "copycat": ("Beginner", "Copies your previous throw after a random opening.", "Its next move is your last move. Counter your own history."),
    "echo_two": ("Beginner", "Copies your throw from two turns ago.", "Use my_history[-2] once two throws have finished."),
    "contrarian": ("Intermediate", "Counters your previous throw after a random opening.", "Predict its counter to your last move, then counter that prediction."),
    "switcheroo": ("Intermediate", "Rock before the halfway point, scissors afterwards.", "A short recent window notices the switch; all-history counts react slowly."),
    "biased_random": ("Intermediate", "Independent throws: 60% rock, 25% paper, 15% scissors.", "Paper has expected net payoff +0.45 per throw."),
    "shifting_bias": ("Intermediate", "Every 50 throws, a new favorite gets probability 70%.", "Try a recent window or discounted counts; compare the delay after each switch."),
    "sticky": ("Intermediate", "80% repeat, 10% each alternative; balanced in the long run.", "Counter its last move. Balanced totals do not imply unpredictable next moves."),
    "win_stay_lose_shift": ("Intermediate", "Repeats after wins/draws; randomly switches after losses.", "After it wins/draws, counter its last move. After it loses, play the move its last move beats."),
    "cycle_counter": ("Advanced", "Counters your most common move over the last ten throws.", "Model its sliding window, including the tie-break from the earliest tied occurrence."),
    "markov": ("Advanced", "Learns what follows your last move and counters that prediction.", "Predict its table from your own history, or remove first-order dependencies."),
    "double_take": ("Advanced", "Nine-throw cycle with balanced single moves and adjacent pairs.", "Try a two-move context; first-order statistics alone miss its deterministic continuation."),
    "sequence_hunter": ("Expert", "Looks for repeated suffixes of length 2-5 in the last 150 throws.", "Use longer-memory tests and independent random exploration; inspect where its predictions fail."),
    "adaptive_ensemble": ("Expert", "Tracks decaying accuracy of repeat, frequency, cycle and reactive predictors.", "Regime changes and mixed policies stress its model selection; measure across fresh seeds."),
    "random_uniform": ("Baseline", "Independent uniform pseudorandom throws.", "A calibration opponent. Do not mistake one lucky series for a reliable exploit."),
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
