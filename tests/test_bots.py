from __future__ import annotations

import importlib
import sys
import types
from enum import Enum
from random import Random

import pytest

from rps_house_bots import get_bot_source, list_bots


@pytest.fixture(autouse=True)
def stub_rpsdk():
    module = types.ModuleType("rpsdk")

    class Move(str, Enum):
        ROCK = "rock"
        PAPER = "paper"
        SCISSORS = "scissors"

        def beats(self, other: "Move") -> bool:
            return (
                (self is Move.ROCK and other is Move.SCISSORS)
                or (self is Move.PAPER and other is Move.ROCK)
                or (self is Move.SCISSORS and other is Move.PAPER)
            )

    module.Move = Move
    sys.modules["rpsdk"] = module

    yield Move

    sys.modules.pop("rpsdk", None)
    for name in [name for name in list(sys.modules) if name.startswith("rps_house_bots.bots.")]:
        sys.modules.pop(name, None)


def test_list_bots_contains_expected_slugs():
    slugs = {spec.slug for spec in list_bots()}
    assert {
        "rocky",
        "cycle_rps",
        "random_uniform",
        "cycle_counter",
        "contrarian",
        "copycat",
        "switcheroo",
        "win_stay_lose_shift",
    } <= slugs


def test_get_bot_source_returns_python_code():
    source = get_bot_source("rocky")
    assert "def next_move" in source


def test_rocky_always_throws_rock(stub_rpsdk):
    module = importlib.import_module("rps_house_bots.bots.rocky")
    assert module.next_move([], [], {}) is stub_rpsdk.ROCK
    assert module.next_move(["paper"], ["rock"], {}) is stub_rpsdk.ROCK


def test_cycle_rps_iterates_moves_in_order(stub_rpsdk):
    module = importlib.import_module("rps_house_bots.bots.cycle_rps")
    module._index = 0  # type: ignore[attr-defined]
    moves = [module.next_move([], [], {}) for _ in range(4)]
    assert moves == [
        stub_rpsdk.ROCK,
        stub_rpsdk.PAPER,
        stub_rpsdk.SCISSORS,
        stub_rpsdk.ROCK,
    ]


def test_random_uniform_respects_match_seed(stub_rpsdk):
    module = importlib.import_module("rps_house_bots.bots.random_uniform")
    rng = Random(99)
    moves = []
    for round_number in range(5):
        moves.append(module.next_move([], [], {"round": round_number, "seed": 99}))
    expected = [rng.choice(list(stub_rpsdk)) for _ in range(5)]
    assert moves == expected


def test_cycle_counter_targets_most_common_recent_move(stub_rpsdk):
    module = importlib.import_module("rps_house_bots.bots.cycle_counter")
    assert module.next_move([], [], {}) == stub_rpsdk.ROCK

    history = [stub_rpsdk.ROCK] * 8 + [stub_rpsdk.PAPER] * 2
    assert module.next_move([], history, {}) == stub_rpsdk.PAPER

    history = [stub_rpsdk.PAPER] * 7 + [stub_rpsdk.SCISSORS] * 3
    assert module.next_move([], history, {}) == stub_rpsdk.SCISSORS


def test_copycat_mirrors_opponents_last_move(stub_rpsdk):
    module = importlib.import_module("rps_house_bots.bots.copycat")
    first_move = module.next_move([], [], {"round": 0, "seed": 123})
    assert first_move in list(stub_rpsdk)
    assert module.next_move([], [stub_rpsdk.SCISSORS], {"round": 1, "seed": 123}) == stub_rpsdk.SCISSORS


def test_contrarian_counters_opponents_last_move(stub_rpsdk):
    module = importlib.import_module("rps_house_bots.bots.contrarian")
    assert module.next_move([], [stub_rpsdk.ROCK], {"round": 1, "seed": 123}) == stub_rpsdk.PAPER
    assert module.next_move([], [stub_rpsdk.PAPER], {"round": 2, "seed": 123}) == stub_rpsdk.SCISSORS
    assert module.next_move([], [stub_rpsdk.SCISSORS], {"round": 3, "seed": 123}) == stub_rpsdk.ROCK


def test_switcheroo_changes_strategy_at_halfway_point(stub_rpsdk):
    module = importlib.import_module("rps_house_bots.bots.switcheroo")
    assert module.next_move([], [], {"round": 0, "best_of": 5}) == stub_rpsdk.ROCK
    assert module.next_move([], [], {"round": 1, "best_of": 5}) == stub_rpsdk.ROCK
    assert module.next_move([], [], {"round": 2, "best_of": 5}) == stub_rpsdk.SCISSORS


def test_win_stay_lose_shift_repeats_after_non_loss_and_switches_after_loss(stub_rpsdk):
    module = importlib.import_module("rps_house_bots.bots.win_stay_lose_shift")
    first_move = module.next_move([], [], {"round": 0, "seed": 321})
    assert first_move in list(stub_rpsdk)
    assert module.next_move([stub_rpsdk.ROCK], [stub_rpsdk.SCISSORS], {"round": 1, "seed": 321}) == stub_rpsdk.ROCK
    switched_move = module.next_move([stub_rpsdk.ROCK], [stub_rpsdk.PAPER], {"round": 2, "seed": 321})
    assert switched_move in {stub_rpsdk.PAPER, stub_rpsdk.SCISSORS}
    assert switched_move != stub_rpsdk.ROCK

