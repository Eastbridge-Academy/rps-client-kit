"""Starter-project helpers for participant bots."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

from rich.console import Console

console = Console()


def initialize_starter_project(destination: Path, *, force: bool = False) -> None:
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)

    bot_path = destination / "bot.py"
    if bot_path.exists() and not force:
        console.print(f"[red]{bot_path} already exists. Use --force to overwrite it.[/red]")
        raise SystemExit(1)

    starter_source = resources.files("rps_client").joinpath("starter", "bot.py").read_text(encoding="utf-8")
    bot_path.write_text(starter_source, encoding="utf-8")

    console.print(f"[green]Starter bot written to {bot_path}[/green]")
    console.print("Next steps:")
    console.print("1. Edit bot.py with your strategy.")
    console.print("2. Run `rps-cli validate` for a local contract check and smoke match.")
    console.print("3. Run `rps-cli submit \"Team Name\"` when you are ready.")
