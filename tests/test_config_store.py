from pathlib import Path

from rps_client.config import ConfigStore


def test_config_store_round_trip(tmp_path: Path):
    config_file = tmp_path / "config.json"
    store = ConfigStore(path=config_file)
    store.token = "abc123"
    store.save()

    reloaded = ConfigStore(path=config_file)
    assert reloaded.token == "abc123"


def test_projects_have_independent_configs(tmp_path, monkeypatch):
    one, two = tmp_path / "one", tmp_path / "two"
    one.mkdir()
    two.mkdir()
    monkeypatch.chdir(one)
    store = ConfigStore()
    store.token = "team-one-token"
    store.league = "workshop"
    store.save()
    monkeypatch.chdir(two)
    assert ConfigStore().token is None
    assert ConfigStore().api_url == "https://arena.eastbrid.ge"
    monkeypatch.chdir(one)
    assert ConfigStore().league == "workshop"


def test_environment_override_is_not_persisted_by_another_setting(tmp_path, monkeypatch):
    import json
    monkeypatch.setenv("RPS_SUBMIT_TOKEN", "environment-secret")
    store = ConfigStore(path=tmp_path / "config.json")
    assert store.token == "environment-secret"
    store.league = "rehearsal"
    store.save()
    assert json.loads(store.path.read_text())["token"] is None
    assert store.path.stat().st_mode & 0o777 == 0o600
