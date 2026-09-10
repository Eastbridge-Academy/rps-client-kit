"""Participant commands: initialize, test, practice, submit, and inspect."""

from importlib.metadata import version
import json
from pathlib import Path
import subprocess
import sys
from typing import Optional

import httpx
import typer
from rich.console import Console
from rich.table import Table

from rps_client.config import ConfigStore
from rps_client.participant_bot import ParticipantBotError
from rps_client.starter import initialize_starter_project
from rps_client.simulator import run_local_simulation
from rps_client.status import show_bot_status
from rps_client.submission import _build_submission_archive, submit_bot_archive
from rps_client.validation import validate_local_bot
from rps_house_bots import list_bots

app = typer.Typer(name="rps-cli", help="Eastbridge RPS participant toolkit", no_args_is_help=True)
config_app = typer.Typer(help="Manage .rps-cli.json in this project.", no_args_is_help=True)
app.add_typer(config_app, name="config")
console = Console()


def _config() -> ConfigStore:
    try:
        return ConfigStore()
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(str(exc)) from exc


@app.callback(invoke_without_command=True)
def main(show_version: bool = typer.Option(False, "--version", is_eager=True, help="Show the installed kit version.")) -> None:
    if show_version:
        typer.echo(f"rps-cli {version('eastbridge-rps-client-kit')}")
        raise typer.Exit()


@app.command("init")
def init_project(
    destination: Path = typer.Argument(Path(".")),
    force: bool = typer.Option(False, "--force", help="Replace scaffold files, including bot.py and tests."),
) -> None:
    """Create a working bot, tests and a short project guide."""
    initialize_starter_project(destination, force=force)


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def test(ctx: typer.Context) -> None:
    """Run project tests; pass pytest options such as -q or -k first_throw."""
    if not Path("tests").is_dir():
        raise typer.BadParameter("No tests/ directory. Run rps-cli init in your bot folder first.")
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "tests", *ctx.args], timeout=60)
    except subprocess.TimeoutExpired as exc:
        typer.echo("Tests exceeded 60 seconds. Check for an infinite loop or slow bot startup.", err=True)
        raise typer.Exit(1) from exc
    raise typer.Exit(result.returncode)


@app.command()
def info() -> None:
    """Show kit version, environment and effective configuration; never print the token."""
    config = _config()
    typer.echo(f"Kit: {version('eastbridge-rps-client-kit')}")
    typer.echo(f"Python: {sys.version.split()[0]} ({sys.executable})")
    typer.echo(f"Project: {Path.cwd()}")
    typer.echo(f"Configuration: {config.path}")
    typer.echo(f"API URL: {config.api_url}")
    typer.echo(f"League: {config.league}")
    typer.echo(f"Submit token: {'configured' if config.token else 'not set'}")
    typer.echo(f"bot.py: {'present' if Path('bot.py').is_file() else 'missing; run rps-cli init'}")


@app.command()
def doctor() -> None:
    """Check the project and reachability of the configured active RPS league."""
    info()
    config = _config()
    problems = []
    if not Path("bot.py").is_file():
        problems.append("Run rps-cli init in your bot folder.")
    if not config.token:
        problems.append("Ask your facilitator for the submit token, then run rps-cli config set token TOKEN.")
    try:
        response = httpx.get(f"{config.api_url}/api/healthz", timeout=5)
        response.raise_for_status()
        response = httpx.get(f"{config.api_url}/api/v1/leagues", timeout=5)
        response.raise_for_status()
        leagues = response.json()
        league = next((item for item in leagues if item["slug"] == config.league), None)
        if not league or league.get("game_type") != "rps" or not league.get("is_active"):
            active = ", ".join(item["slug"] for item in leagues if item.get("game_type") == "rps") or "none"
            problems.append(f"Choose an active RPS league with rps-cli config set league SLUG. Available: {active}.")
        else:
            typer.echo(f"Server reachable; {league['name']} is active.")
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        problems.append(f"Could not check the server ({type(exc).__name__}). Check api_url and your connection.")
    for problem in problems:
        typer.echo(problem, err=True)
    if problems:
        raise typer.Exit(1)
    typer.echo("Ready for local tests and submission. The server validates the token when you submit.")


@app.command()
def opponents(hints: bool = typer.Option(False, "--hints", help="Include strategy suggestions.")) -> None:
    """Meet the built-in practice field."""
    table = Table(title="House bots")
    table.add_column("Slug", style="cyan")
    table.add_column("Route")
    table.add_column("Personality")
    if hints:
        table.add_column("Try this")
    for spec in list_bots():
        row = [spec.slug, spec.level, spec.description]
        if hints:
            row.append(spec.hint)
        table.add_row(*row)
    console.print(table)


@app.command()
def play(
    against: Optional[str] = typer.Option(None, "--against", help="Comma-separated house bot slugs; default: the whole field."),
    bot_path: Path = typer.Option(Path("bot.py"), "--bot", help="Participant entry file."),
    best_of: int = typer.Option(501, "--best-of", min=1, max=10001, help="Fixed number of throws, including draws."),
    seed: int = typer.Option(42, "--seed", help="First practice seed."),
    games: int = typer.Option(1, "--games", min=1, max=100, help="Matches per opponent, using consecutive seeds."),
    output: Optional[Path] = typer.Option(None, "--output", help="Save results and all observed throws as JSON."),
    timeout: float = typer.Option(30, "--timeout", min=1, max=600, help="Whole-match practice timeout in seconds."),
) -> None:
    """Practice with fresh bot instances and reproducible seeds."""
    try:
        results = run_local_simulation(
            opponent_names=against.split(",") if against is not None else None,
            best_of=best_of, bot_path=bot_path, seed=seed, games=games,
            record=output is not None, timeout=timeout,
        )
    except (ParticipantBotError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    if output is not None:
        from dataclasses import asdict
        output.write_text(json.dumps({"kit_version": version("eastbridge-rps-client-kit"),
                                      "matches": [asdict(result) for result in results]}, indent=2) + "\n", encoding="utf-8")
        typer.echo(f"Saved {output}")
    if any(result.errors for result in results):
        typer.echo("Bot errors occurred. Fix them before submitting.", err=True)
        raise typer.Exit(1)


@app.command("validate")
def validate(
    bot_path: Path = typer.Argument(Path("bot.py")),
    against: str = typer.Option("rocky,copycat", "--against", help="Comma-separated smoke-test opponents."),
    best_of: int = typer.Option(9, "--best-of", min=1, max=10001, help="Smoke-test series length."),
    smoke: bool = typer.Option(True, "--smoke/--no-smoke", help="Run smoke matches after the contract check."),
) -> None:
    """Check the bot contract and play short smoke matches."""
    try:
        validate_local_bot(bot_path=bot_path, smoke_opponents=against.split(","), best_of=best_of, smoke=smoke)
    except (ParticipantBotError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc


@app.command()
def package(
    output: Path = typer.Option(Path("submission.zip"), "--output", help="Local archive destination."),
    bot_path: Path = typer.Option(Path("bot.py"), "--bot", help="Participant entry file."),
) -> None:
    """Build the exact submission archive without contacting the arena."""
    import io
    import zipfile
    try:
        archive = _build_submission_archive(bot_path)
        output.write_bytes(archive)
    except (OSError, ParticipantBotError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    with zipfile.ZipFile(io.BytesIO(archive)) as zf:
        for name in zf.namelist():
            typer.echo(name)
    typer.echo(f"Saved {output} ({len(archive)} bytes); nothing was uploaded.")


@app.command()
def submit(
    team_name: str,
    bot_path: Path = typer.Argument(Path("bot.py")),
    notes: Optional[str] = typer.Option(None, "--notes", help="Optional notes for staff."),
    email: Optional[str] = typer.Option(None, "--email", help="Optional contact email for staff."),
) -> None:
    """Upload a bot version for server validation; reuse your team name."""
    submit_bot_archive(team_name=team_name, bot_path=bot_path, notes=notes, email=email, config=_config())


@app.command()
def status(team_name: str) -> None:
    """Check whether the latest submission is active or needs a fix."""
    show_bot_status(team_name=team_name, config=_config())


@config_app.command("set")
def config_set(key: str, value: str) -> None:
    """Save api_url, league or token in this project's .rps-cli.json."""
    config = _config()
    try:
        config.set(key, value)
        config.save()
    except (ValueError, OSError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Saved {key} in {config.path.name}.")


@config_app.command("get")
def config_get(key: str) -> None:
    """Read an effective setting. Tokens are masked."""
    config = _config()
    if key not in {"api_url", "league", "token"}:
        raise typer.BadParameter("Choose api_url, league, or token.")
    value = getattr(config, key)
    typer.echo(("<configured>" if value else "<unset>") if key == "token" else value)


if __name__ == "__main__":
    app()
