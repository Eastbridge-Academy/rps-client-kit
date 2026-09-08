from __future__ import annotations

import importlib
import sys
from random import Random

import pytest

from rps_house_bots import get_bot_source, list_bots


@pytest.fixture(autouse=True)
def move_type():
    from rpsdk import Move
    yield Move
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


def test_rocky_always_throws_rock(move_type):
    module = importlib.import_module("rps_house_bots.bots.rocky")
    assert module.next_move([], [], {}) is move_type.ROCK
    assert module.next_move(["paper"], ["rock"], {}) is move_type.ROCK


def test_cycle_rps_iterates_moves_in_order(move_type):
    module = importlib.import_module("rps_house_bots.bots.cycle_rps")
    module._index = 0  # type: ignore[attr-defined]
    moves = [module.next_move([], [], {}) for _ in range(4)]
    assert moves == [
        move_type.ROCK,
        move_type.PAPER,
        move_type.SCISSORS,
        move_type.ROCK,
    ]


def test_random_uniform_respects_match_seed(move_type):
    module = importlib.import_module("rps_house_bots.bots.random_uniform")
    rng = Random(99)
    moves = []
    for round_number in range(5):
        moves.append(module.next_move([], [], {"round": round_number, "seed": 99}))
    expected = [rng.choice(list(move_type)) for _ in range(5)]
    assert moves == expected


def test_cycle_counter_targets_most_common_recent_move(move_type):
    module = importlib.import_module("rps_house_bots.bots.cycle_counter")
    assert module.next_move([], [], {}) == move_type.ROCK

    history = [move_type.ROCK] * 8 + [move_type.PAPER] * 2
    assert module.next_move([], history, {}) == move_type.PAPER

    history = [move_type.PAPER] * 7 + [move_type.SCISSORS] * 3
    assert module.next_move([], history, {}) == move_type.SCISSORS


def test_copycat_mirrors_opponents_last_move(move_type):
    module = importlib.import_module("rps_house_bots.bots.copycat")
    first_move = module.next_move([], [], {"round": 0, "seed": 123})
    assert first_move in list(move_type)
    assert module.next_move([], [move_type.SCISSORS], {"round": 1, "seed": 123}) == move_type.SCISSORS


def test_contrarian_counters_opponents_last_move(move_type):
    module = importlib.import_module("rps_house_bots.bots.contrarian")
    assert module.next_move([], [move_type.ROCK], {"round": 1, "seed": 123}) == move_type.PAPER
    assert module.next_move([], [move_type.PAPER], {"round": 2, "seed": 123}) == move_type.SCISSORS
    assert module.next_move([], [move_type.SCISSORS], {"round": 3, "seed": 123}) == move_type.ROCK


def test_switcheroo_changes_strategy_at_halfway_point(move_type):
    module = importlib.import_module("rps_house_bots.bots.switcheroo")
    assert module.next_move([], [], {"round": 0, "best_of": 5}) == move_type.ROCK
    assert module.next_move([], [], {"round": 1, "best_of": 5}) == move_type.ROCK
    assert module.next_move([], [], {"round": 2, "best_of": 5}) == move_type.SCISSORS


def test_win_stay_lose_shift_repeats_after_non_loss_and_switches_after_loss(move_type):
    module = importlib.import_module("rps_house_bots.bots.win_stay_lose_shift")
    first_move = module.next_move([], [], {"round": 0, "seed": 321})
    assert first_move in list(move_type)
    assert module.next_move([move_type.ROCK], [move_type.SCISSORS], {"round": 1, "seed": 321}) == move_type.ROCK
    switched_move = module.next_move([move_type.ROCK], [move_type.PAPER], {"round": 2, "seed": 321})
    assert switched_move in {move_type.PAPER, move_type.SCISSORS}
    assert switched_move != move_type.ROCK



@pytest.mark.parametrize("slug", ["markov", "sequence_hunter", "adaptive_ensemble"])
def test_predictors_exploit_a_cycle(slug, move_type):
    bot = importlib.import_module(f"rps_house_bots.bots.{slug}")
    bot.setup({"seed": 1729})
    mine, theirs = [], []
    wins = 0
    for index in range(100):
        move = bot.next_move(list(mine), list(theirs), {"round": index, "best_of": 100})
        opponent = list(move_type)[index % 3]
        wins += move.beats(opponent)
        mine.append(move)
        theirs.append(opponent)
    assert wins >= 80


@pytest.mark.parametrize("slug", ["biased_random", "shifting_bias", "markov", "sequence_hunter", "adaptive_ensemble"])
def test_new_bots_repeat_with_same_seed(slug, move_type):
    bot = importlib.import_module(f"rps_house_bots.bots.{slug}")
    def run():
        bot.setup({"seed": 72})
        mine, theirs = [], []
        for index in range(120):
            mine.append(bot.next_move(list(mine), list(theirs), {"round": index, "best_of": 120}))
            theirs.append(list(move_type)[index % 3])
        return mine
    assert run() == run()
