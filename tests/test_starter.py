from __future__ import annotations


from rps_client.starter import initialize_starter_project


def test_initialize_starter_project_writes_bot_file(tmp_path, capsys):
    initialize_starter_project(tmp_path)

    out = capsys.readouterr().out
    assert (tmp_path / "bot.py").exists()
    assert "Starter project ready" in out
    assert "rps-cli validate" in out


def test_initialize_starter_project_preserves_edits_unless_forced(tmp_path):
    bot_path = tmp_path / "bot.py"
    bot_path.write_text("print('custom')\n")

    initialize_starter_project(tmp_path)
    assert bot_path.read_text() == "print('custom')\n"
    assert (tmp_path / "tests/test_bot.py").is_file()
    initialize_starter_project(tmp_path, force=True)
    assert "This baseline is legal" in bot_path.read_text()
