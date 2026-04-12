from __future__ import annotations

import pytest

from rps_client.starter import initialize_starter_project


def test_initialize_starter_project_writes_bot_file(tmp_path, capsys):
    initialize_starter_project(tmp_path)

    out = capsys.readouterr().out
    assert (tmp_path / "bot.py").exists()
    assert "Starter bot written" in out
    assert "rps-cli validate" in out


def test_initialize_starter_project_requires_force_to_overwrite(tmp_path):
    bot_path = tmp_path / "bot.py"
    bot_path.write_text("print('custom')\n")

    with pytest.raises(SystemExit):
        initialize_starter_project(tmp_path)

    initialize_starter_project(tmp_path, force=True)
    assert "Default implementation" in bot_path.read_text()
