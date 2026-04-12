"""Submission logic for uploading bots to the tournament API."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import Iterable, Tuple

import httpx
from rich.console import Console

from rps_client.config import ConfigStore

console = Console()


def submit_bot_archive(
    *,
    team_name: str,
    bot_path: Path,
    notes: str | None,
    email: str | None = None,
    config: ConfigStore,
) -> None:
    token = config.token
    if not token:
        console.print("[red]No submit token configured. Run `rps-cli config set token <TOKEN>` or set `RPS_SUBMIT_TOKEN` first.")
        raise SystemExit(1)

    if not bot_path.exists():
        console.print(f"[red]Bot file {bot_path} does not exist." )
        raise SystemExit(1)

    archive_bytes = _build_submission_archive(bot_path)

    url = config.api_url.rstrip("/") + "/api/v1/bots/submit"

    form_data = {"team_name": team_name}
    if notes:
        form_data["notes"] = notes
    if email:
        form_data["email"] = email

    try:
        response = httpx.post(
            url,
            headers={"X-Submit-Token": token},
            data=form_data,
            files={"archive": ("submission.zip", archive_bytes, "application/zip")},
            timeout=10.0,
        )
    except httpx.HTTPError as exc:
        console.print(f"[red]Failed to contact API: {exc}")
        raise SystemExit(1) from exc

    if response.status_code != 202:
        detail = response.text
        try:
            detail = response.json().get("detail", detail)
        except Exception:
            pass
        console.print(f"[red]Submission failed ({response.status_code}): {detail}")
        raise SystemExit(1)

    message = "Submission uploaded and queued for validation."
    try:
        message = response.json().get("message", message)
    except Exception:
        pass
    console.print(f"[green]{message}")
    console.print(f'Check progress with: rps-cli status "{team_name}"')


def _build_submission_archive(bot_path: Path) -> bytes:
    bot_path = bot_path.resolve()
    root = bot_path.parent
    files_to_include = _gather_files(root, bot_path.name)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(bot_path, arcname="bot.py")
        for arcname, file_path in files_to_include:
            if file_path == bot_path:
                continue
            zf.write(file_path, arcname=arcname)
    return buffer.getvalue()


def _gather_files(root: Path, bot_filename: str) -> Iterable[Tuple[str, Path]]:
    """Collect additional files to package with the submission."""
    entries: list[Tuple[str, Path]] = []

    optional_files = ["README.md", "README.txt"]
    for name in optional_files:
        candidate = root / name
        if candidate.exists() and candidate.is_file():
            entries.append((candidate.relative_to(root).as_posix(), candidate))

    for py_file in root.glob("*.py"):
        if py_file.name != bot_filename and py_file.is_file():
            entries.append((py_file.relative_to(root).as_posix(), py_file))

    data_dir = root / "data"
    if data_dir.exists():
        for path in data_dir.rglob("*"):
            if path.is_file():
                entries.append((path.relative_to(root).as_posix(), path))

    return entries
