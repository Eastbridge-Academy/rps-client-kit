import rpsdk
import pytest
from rps_client.simulator import (
    AVAILABLE_BOTS,
    _load_house_bot,
    _simulate_series,
    run_local_simulation,
)
from rps_house_bots import list_bots


def test_run_local_simulation(tmp_path, monkeypatch, capsys):
    bot_code = """
import rpsdk

def next_move(my_history, opponent_history, match_state):
    return rpsdk.Move.ROCK
"""
    bot_file = tmp_path / "bot.py"
    bot_file.write_text(bot_code)

    monkeypatch.chdir(tmp_path)

    run_local_simulation(["random_uniform"], best_of=9)

    out = capsys.readouterr().out
    assert "random_uniform" in out
    assert "Random Uniform" in out
    assert "Win" in out or "Loss" in out or "Draw" in out
    assert "Errors" in out


def test_run_local_simulation_with_unknown_opponent(tmp_path, monkeypatch, capsys):
    (tmp_path / "bot.py").write_text(
        """
import rpsdk

def next_move(my_history, opponent_history, match_state):
    return rpsdk.Move.ROCK
"""
    )
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="Unknown opponent 'does_not_exist'"):
        run_local_simulation(["does_not_exist"], best_of=3)


def test_load_house_bot_produces_legal_move():
    spec = next(spec for spec in list_bots() if spec.slug in AVAILABLE_BOTS)
    bot = _load_house_bot(spec, seed=123)
    move = bot.next_move(
        my_history=[rpsdk.Move.PAPER, rpsdk.Move.ROCK],
        opponent_history=[rpsdk.Move.ROCK, rpsdk.Move.SCISSORS],
        match_state={"round": 2, "best_of": 5, "seed": 123, "timeouts": 0, "opponent_timeouts": 0},
    )
    assert isinstance(move, rpsdk.Move)


def test_simulation_counts_errors(tmp_path, monkeypatch):
    (tmp_path / "bot.py").write_text(
        """
import rpsdk

def next_move(my_history, opponent_history, match_state):
    raise ValueError("boom")
"""
    )
    monkeypatch.chdir(tmp_path)

    spec = next(spec for spec in list_bots() if spec.slug in AVAILABLE_BOTS)
    opponent = _load_house_bot(spec, seed=321)

    def participant(my_history, opponent_history, match_state):
        raise ValueError("boom")

    result = _simulate_series(participant, opponent, best_of=7, seed=321)
    assert result.errors == 7


def test_each_opponent_gets_fresh_setup_and_globals(tmp_path):
    bot = tmp_path / "bot.py"
    (tmp_path / "helper.py").write_text("calls = 0\n")
    bot.write_text('''
from rpsdk import Move
import helper
calls = 0
ready = False
def setup(config):
    global ready
    ready = True
def next_move(my_history, opponent_history, match_state):
    global calls
    assert ready
    assert calls == helper.calls == match_state["round"]
    calls += 1
    helper.calls += 1
    return Move.PAPER
''')
    results = run_local_simulation(["rocky", "copycat"], best_of=3, bot_path=bot)
    assert len(results) == 2
    assert all(result.errors == 0 for result in results)

def test_last_outcome_is_previous_throw_and_both_players_see_only_past_moves():
    from types import ModuleType
    from rps_client.simulator import LoadedHouseBot
    from rps_house_bots import BotSpec
    mine_states, their_states = [], []
    def participant(mine, theirs, state):
        assert len(mine) == len(theirs) == state["round"]
        mine_states.append(state["last_outcome"])
        return [rpsdk.Move.PAPER, rpsdk.Move.PAPER, rpsdk.Move.SCISSORS, rpsdk.Move.ROCK][state["round"]]
    def opponent(mine, theirs, state):
        assert len(mine) == len(theirs) == state["round"]
        their_states.append(state["last_outcome"])
        return rpsdk.Move.ROCK
    module = ModuleType("observing_bot")
    module.next_move = opponent
    result = _simulate_series(participant, LoadedHouseBot(BotSpec("rocky"), module, 12), best_of=4, seed=12, record=True)
    assert mine_states == [None, "win", "win", "loss"]
    assert their_states == [None, "loss", "loss", "win"]
    assert (result.wins, result.losses, result.draws) == (2, 1, 1)
    assert [row["outcome"] for row in result.rounds] == [1, 1, -1, 0]


def test_repeated_seeds_reproduce_practice_and_reset_helpers(tmp_path):
    bot = tmp_path / "bot.py"
    bot.write_text("import random\ndef next_move(*args): return random.choice(['rock','paper','scissors'])\n")
    first = run_local_simulation(["sticky"], best_of=30, bot_path=bot, games=2, seed=81, record=True)
    second = run_local_simulation(["sticky"], best_of=30, bot_path=bot, games=2, seed=81, record=True)
    assert first == second
    assert first[0].rounds != first[1].rounds


def test_practice_kills_a_stuck_bot(tmp_path):
    from rps_client.participant_bot import ParticipantBotError
    bot = tmp_path / "bot.py"
    bot.write_text("def next_move(*args):\n    while True: pass\n")
    with pytest.raises(ParticipantBotError, match="exceeded"):
        run_local_simulation(["rocky"], best_of=3, bot_path=bot, timeout=.5)
