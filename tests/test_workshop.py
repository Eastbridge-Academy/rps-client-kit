"""Checks for the actual lesson calculations, code and facilitator examples."""
from collections import Counter, defaultdict
import importlib.util
import math
from pathlib import Path
import re
import sys

import pytest

from rps_client.participant_bot import load_participant_bot
from rps_client.simulator import AVAILABLE_BOTS, _load_house_bot, _simulate_series
from rpsdk import Move

WORKSHOP = Path(__file__).resolve().parents[1] / "workshop"
SOLUTIONS = WORKSHOP / "solutions"
spec = importlib.util.spec_from_file_location("lesson_models", SOLUTIONS / "lesson_models/__init__.py")
models = importlib.util.module_from_spec(spec)
sys.modules["lesson_models"] = models
spec.loader.exec_module(models)
R, P, S = tuple(Move)


def test_payoff_response_is_not_countering_the_most_likely_move():
    q = (.40, .21, .39)
    values = [sum(p * models.payoff(action, opposing) for p, opposing in zip(q, Move)) for action in Move]
    assert values == pytest.approx([.18, .01, -.19])
    assert models.best_response(q) == (1, 0, 0)
    assert models.best_response(models.UNIFORM) == pytest.approx(models.UNIFORM)


def test_incremental_transition_counts_match_rebuild_after_every_observation():
    history = [R, R, P, R, S, P, P, S, S] * 5
    model = models.ContextCounts(2)
    for length in range(len(history) + 1):
        prefix = history[:length]
        model.observe(prefix)
        model.observe(prefix)  # a repeated call must not double-count
        for order in range(3):
            expected = defaultdict(Counter)
            for index in range(order, length):
                expected[tuple(prefix[index - order:index])][prefix[index]] += 1
            assert dict(model.rows[order]) == dict(expected)
        assert sum(model.predict(prefix)) == pytest.approx(1)
    model.observe([])
    assert model.seen == 0 and not any(model.rows)


def test_double_take_has_uniform_order_one_rows_and_deterministic_order_two():
    cycle = [R, R, P, R, S, P, P, S, S]
    rows = defaultdict(Counter)
    successors = defaultdict(set)
    for index in range(9):
        rows[cycle[index]][cycle[(index + 1) % 9]] += 1
        successors[(cycle[index], cycle[(index + 1) % 9])].add(cycle[(index + 2) % 9])
    assert all(row == {R: 1, P: 1, S: 1} for row in rows.values())
    assert len(successors) == 9 and all(len(values) == 1 for values in successors.values())


def test_portfolio_scores_stored_predictions_before_learning_new_answer():
    portfolio = models.Portfolio()
    assert portfolio.probabilities([], []) == pytest.approx(models.UNIFORM)
    portfolio.probabilities([R], [R])
    assert portfolio.logs == pytest.approx([0] * 8)  # uniform opening gains
    stored = tuple(portfolio.pending)
    portfolio.probabilities([R, P], [R, S])
    expected = [portfolio.eta * sum(p * models.payoff(a, S) for p, a in zip(proposal, Move)) for proposal in stored]
    assert portfolio.logs == pytest.approx(expected)
    portfolio.probabilities([R, P], [R, S])
    assert portfolio.logs == pytest.approx(expected)
    portfolio.logs = [10000, -10000, 9000, 5, 0, 0, 0, 0]
    probabilities = portfolio.probabilities([R, P], [R, S])
    assert all(math.isfinite(p) and p >= 0 for p in probabilities)
    assert sum(probabilities) == pytest.approx(1)


def test_terminal_controller_matches_hand_calculation_and_changes_objective():
    controller = models.TerminalController((.3, .6, .1))
    assert [controller.value(0, d) for d in (-1, 0, 1)] == [0, .5, 1]
    assert controller.values(1, 0) == pytest.approx((.25, .6, .65))
    assert controller.values(1, 1) == pytest.approx((.7, .95, .85))
    assert controller.values(1, -1) == pytest.approx((.05, .15, .3))
    assert controller.choose(1, 1) == P
    assert models.best_response((.3, .6, .1)) == (0, 0, 1)
    assert controller.value(30, 31) == 1
    assert controller.value(30, -31) == 0
    assert controller.value(2, 0) == pytest.approx(max(sum(p * max(controller.values(1, models.payoff(a, b)))
                                                        for p, b in zip(controller.q, Move)) for a in Move))


def test_actual_beginner_handout_cycle_snippet_wins_all_501_throws():
    blocks = re.findall(r"\\begin\{lstlisting\}\[style=python[^\]]*\]\n(.*?)\\end\{lstlisting\}", (WORKSHOP / "latex/01-beginner.tex").read_text(), re.S)
    namespace = {"Move": Move}
    dictionary = next(block for block in blocks if block.startswith("COUNTER ="))
    function = next(block for block in blocks if block.startswith("def next_move"))
    exec(dictionary + "\n" + function, namespace)
    result = _simulate_series(namespace["next_move"], _load_house_bot(AVAILABLE_BOTS["cycle_rps"], seed=9), best_of=501, seed=9)
    assert (result.wins, result.losses, result.draws, result.errors) == (501, 0, 0, 0)


@pytest.mark.parametrize("name", ["beginner", "intermediate", "advanced", "expert", "terminal"])
def test_reference_bots_complete_full_series_and_reset_state(name):
    loaded = load_participant_bot(SOLUTIONS / f"{name}.py")
    for slug in AVAILABLE_BOTS:
        loaded.setup({"seed": 41})
        first = _simulate_series(loaded.next_move, _load_house_bot(AVAILABLE_BOTS[slug], seed=97), best_of=501, seed=41)
        loaded.setup({"seed": 41})
        second = _simulate_series(loaded.next_move, _load_house_bot(AVAILABLE_BOTS[slug], seed=97), best_of=501, seed=41)
        assert first == second
        assert first.errors == 0
        assert first.wins + first.losses + first.draws == 501
        if name == "advanced" and slug == "double_take":
            assert first.wins >= 460
