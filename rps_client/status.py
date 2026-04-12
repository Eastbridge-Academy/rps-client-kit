"""Participant-facing status lookup helpers."""

from __future__ import annotations

import httpx
from rich.console import Console

from rps_client.config import ConfigStore

console = Console()


def show_bot_status(*, team_name: str, config: ConfigStore) -> None:
    team_name = team_name.strip()
    if not team_name:
        console.print("[red]Team name is required.")
        raise SystemExit(1)

    base_url = config.api_url.rstrip("/")

    try:
        bots_response = httpx.get(f"{base_url}/api/v1/bots", timeout=10.0)
        bots_response.raise_for_status()
    except httpx.HTTPError as exc:
        console.print(f"[red]Failed to load bot roster: {exc}")
        raise SystemExit(1) from exc

    bots = bots_response.json()
    bot = next((entry for entry in bots if entry["team_name"].casefold() == team_name.casefold()), None)
    if bot is None:
        console.print(f"[red]No bot found for team '{team_name}'.")
        raise SystemExit(1)

    try:
        status_response = httpx.get(f"{base_url}/api/v1/bots/{bot['id']}/status", timeout=10.0)
        status_response.raise_for_status()
    except httpx.HTTPError as exc:
        console.print(f"[red]Failed to load bot status: {exc}")
        raise SystemExit(1) from exc

    payload = status_response.json()
    latest = payload.get("latest_version")
    active = payload.get("active_version")

    console.print(f"[bold]{payload['team_name']}[/bold]")
    console.print(f"Operator status: {payload['operator_status']}")
    if active:
        console.print(f"Active version: v{active['version']} ({active['status']})")
    else:
        console.print("Active version: none")

    if latest:
        console.print(f"Latest version: v{latest['version']} ({latest['status']})")
        if latest.get("rejection_reason"):
            console.print(f"Rejection reason: {latest['rejection_reason']}")
        guidance = _status_guidance(latest_status=latest["status"], rejection_reason=latest.get("rejection_reason"))
        if guidance:
            console.print(guidance)
    else:
        console.print("Latest version: none")


def _status_guidance(*, latest_status: str, rejection_reason: str | None) -> str | None:
    if latest_status == "uploaded":
        return "Status note: upload received and waiting for the validation worker."
    if latest_status == "validating":
        return "Status note: validation is currently running."
    if latest_status == "rejected":
        if rejection_reason:
            return "Status note: fix the rejection reason locally, rerun `rps-cli validate`, then submit again."
        return "Status note: validation failed. Rerun `rps-cli validate` before submitting again."
    if latest_status == "active":
        return "Status note: your latest version is active in the tournament."
    return None
