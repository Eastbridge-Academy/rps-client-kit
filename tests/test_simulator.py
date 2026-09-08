import rpsdk
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

    run_local_simulation(["does_not_exist"], best_of=3)
    out = capsys.readouterr().out
    assert "Unknown opponent 'does_not_exist'" in out


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
