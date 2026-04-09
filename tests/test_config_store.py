from pathlib import Path

from rps_client.config import ConfigStore


def test_config_store_round_trip(tmp_path: Path):
    config_file = tmp_path / "config.json"
    store = ConfigStore(path=config_file)
    store.token = "abc123"
    store.save()

    reloaded = ConfigStore(path=config_file)
    assert reloaded.token == "abc123"

