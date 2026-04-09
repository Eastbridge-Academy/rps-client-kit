"""Typer-based CLI entrypoint."""

from pathlib import Path
from typing import Optional

import typer

from rps_client.config import ConfigStore
from rps_client.simulator import run_local_simulation
from rps_client.submission import submit_bot_archive

app = typer.Typer(name="rps-cli", help="Eastbridge RPS participant toolkit")
config = ConfigStore()
config_app = typer.Typer(help="Manage local CLI configuration.")
app.add_typer(config_app, name="config")


@app.command()
def info() -> None:
    """Show current configuration."""
    token = config.token
    if token:
        typer.echo(f"Submit token: {token[:4]}...{token[-4:]}")
    else:
        typer.echo("Submit token not set. Use `rps-cli config set token <TOKEN>` or set `RPS_SUBMIT_TOKEN`.")
    typer.echo(f"API URL: {config.api_url}")


@app.command()
def submit(
    team_name: str,
    bot_path: Path = typer.Argument(Path("bot.py")),
    notes: Optional[str] = typer.Option(None, "--notes", help="Optional notes displayed to staff"),
    email: Optional[str] = typer.Option(None, "--email", help="Optional contact email for staff"),
) -> None:
    """Submit the current bot to the tournament server."""
    submit_bot_archive(team_name=team_name, bot_path=bot_path, notes=notes, email=email, config=config)


@app.command()
def play(against: Optional[str] = typer.Option(None, help="Comma separated list of built-in opponents")) -> None:
    """Run a quick local simulation against built-in bots."""
    run_local_simulation(opponent_names=against.split(",") if against else None)


@app.command()
def status() -> None:
    """Show latest submission status."""
    typer.echo("Status feature TBD")


@config_app.command("set")
def config_set(key: str, value: str) -> None:
    """Set a configuration key."""
    key = key.lower()
    if key == "token":
        config.token = value.strip()
        config.save()
        typer.echo("Token saved.")
        return
    if key in {"api_url", "url"}:
        config.api_url = value.strip()
        config.save()
        typer.echo("API URL saved.")
        return
    raise typer.BadParameter("Unsupported config key")


@config_app.command("get")
def config_get(key: str) -> None:
    """Get a configuration value."""
    key = key.lower()
    if key == "token":
        typer.echo(config.token or "<unset>")
        return
    if key in {"api_url", "url"}:
        typer.echo(config.api_url)
        return
    raise typer.BadParameter("Unsupported config key")


if __name__ == "__main__":
    app()
