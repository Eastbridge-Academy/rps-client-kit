"""Starter-project helpers for participant bots."""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from rich.console import Console

console = Console()
SCAFFOLD_FILES = ("bot.py", "README.md", "tests/test_bot.py")


def initialize_starter_project(destination: Path, *, force: bool = False) -> None:
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    source_root = resources.files("rps_client").joinpath("starter")
    for relative in SCAFFOLD_FILES:
        target = destination / relative
        if target.exists() and not force:
            console.print(f"Keeping {relative} (use --force to replace scaffold files).")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source_root.joinpath(relative).read_text(encoding="utf-8"), encoding="utf-8")
        console.print(f"Wrote {relative}")
    ignore = destination / ".gitignore"
    existing = ignore.read_text(encoding="utf-8") if ignore.exists() else ""
    additions = [line for line in (".rps-cli.json", ".venv/", "__pycache__/", ".pytest_cache/")
                 if line not in existing.splitlines()]
    if additions:
        ignore.write_text(existing.rstrip() + "\n" + "\n".join(additions) + "\n", encoding="utf-8")
    console.print(f"[green]Starter project ready in {destination}[/green]")
    console.print("Next: rps-cli test, then rps-cli validate.")
    console.print("Explore the field with rps-cli opponents; edit bot.py and practice with rps-cli play.")
