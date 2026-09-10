"""Exercise project and uv-tool installs on Windows, macOS and Linux.

Run after uv build, or supply a wheel URL / tagged Git URL as the argument.
All environments and participant projects are created in a temporary directory.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str | Path], cwd: Path, env: dict[str, str]) -> None:
    subprocess.run([str(arg) for arg in args], cwd=cwd, env=env, check=True, timeout=180)


def exercise(cli: Path, project: Path, env: dict[str, str]) -> None:
    project.mkdir(parents=True, exist_ok=True)
    for args in (
        ["--version"],
        ["init"],
        ["test"],
        ["validate", "--against", "rocky", "--best-of", "9"],
        ["play", "--against", "rocky,sticky,double_take", "--best-of", "501",
         "--seed", "42", "--output", "practice.json"],
        ["package", "--output", "submission.zip"],
    ):
        run([cli, *args], project, env)
    matches = json.loads((project / "practice.json").read_text())["matches"]
    assert len(matches) == 3
    assert all(len(match["rounds"]) == 501 and match["errors"] == 0 for match in matches)
    with ZipFile(project / "submission.zip") as archive:
        assert {"bot.py", "rpsdk/__init__.py"} <= set(archive.namelist())
        assert not any(".venv" in name or ".rps-cli.json" in name for name in archive.namelist())
        archive.extractall(project / "unpacked")
    run([cli, "validate", "unpacked/bot.py", "--no-smoke"], project, env)
    bot = project / "bot.py"
    bot.write_bytes(bot.read_bytes() + b"\n# participant edit\n")
    original = bot.read_bytes()
    run([cli, "init"], project, env)
    assert bot.read_bytes() == original


def main() -> None:
    version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", default=str(
        ROOT / f"dist/eastbridge_rps_client_kit-{version}-py3-none-any.whl"))
    args = parser.parse_args()
    uv = shutil.which("uv")
    if uv is None:
        raise SystemExit("Install uv before running this check")
    env = dict(os.environ)
    for key in ("VIRTUAL_ENV", "PYTHONPATH", "PYTHONHOME"):
        env.pop(key, None)
    env["UV_NO_PROGRESS"] = "1"
    with tempfile.TemporaryDirectory(prefix="rps-install-") as directory:
        root = Path(directory)
        project = root / "project with spaces"
        project.mkdir()
        venv = project / ".venv"
        scripts = venv / ("Scripts" if os.name == "nt" else "bin")
        executable = "rps-cli.exe" if os.name == "nt" else "rps-cli"
        python = scripts / ("python.exe" if os.name == "nt" else "python")
        run([uv, "venv", "--python", sys.executable, venv], root, env)
        run([uv, "pip", "install", "--python", python, args.source], root, env)
        exercise(scripts / executable, project, env)

        env["UV_TOOL_DIR"] = str(root / "tools")
        env["UV_TOOL_BIN_DIR"] = str(root / "tool-bin")
        run([uv, "tool", "install", "--python", sys.executable, args.source], root, env)
        exercise(root / "tool-bin" / executable, root / "tool project with spaces", env)
    print("Project and uv-tool installs passed: starter tests, validation, 3,006 throws, packaging and preserved edits.")


if __name__ == "__main__":
    main()
