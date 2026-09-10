"""Submission logic for uploading bots to the tournament API."""

from __future__ import annotations

import ast
import io
import zipfile
from collections.abc import Iterable
from importlib import resources
from pathlib import Path

import httpx
from rich.console import Console

from rps_client.config import ConfigStore
from rps_client.participant_bot import ParticipantBotError

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

    if not team_name.strip():
        console.print("Team name is required.", style="red")
        raise SystemExit(1)
    try:
        archive_bytes = _build_submission_archive(bot_path)
    except (ParticipantBotError, OSError) as exc:
        console.print(str(exc), style="red", markup=False)
        raise SystemExit(1) from exc

    # Every league-scoped resource lives under /api/v1/leagues/{slug}/ on
    # the arena; there is deliberately no league-defaulting flat route.
    url = config.api_url.rstrip("/") + f"/api/v1/leagues/{config.league}/bots/submit"

    form_data = {"team_name": team_name}
    if notes:
        form_data["notes"] = notes
    if email:
        form_data["email"] = email

    try:
        response = httpx.post(
            url,
            headers={"Authorization": f"Bearer {token}"},
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
        zf.writestr("rpsdk/__init__.py", resources.files("rpsdk").joinpath("__init__.py").read_text(encoding="utf-8"))
    return buffer.getvalue()


def _gather_files(root: Path, bot_filename: str) -> Iterable[tuple[str, Path]]:
    """Collect imported local modules/packages and explicitly supplied data.

    Reading imports never executes participant code. A package includes all its
    Python files, including modules imported relatively or dynamically within it.
    Arbitrary top-level dynamic imports cannot be inferred; package them normally.
    """
    root = root.resolve()
    collected: dict[str, Path] = {}
    pending = [root / bot_filename]
    visited = set()

    def include(path: Path) -> None:
        if not path.resolve().is_relative_to(root):
            raise ParticipantBotError(f"Submission file leaves the project through a symlink: {path.name}")
        collected[path.relative_to(root).as_posix()] = path

    while pending:
        source = pending.pop()
        if source in visited:
            continue
        visited.add(source)
        include(source)
        try:
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        except (SyntaxError, UnicodeError) as exc:
            raise ParticipantBotError(f"Cannot package {source.name}: {exc}") from exc
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names.add(node.module.split(".")[0])
        for name in names:
            module = root / f"{name}.py"
            package = root / name
            if name == "rpsdk" and (module.exists() or package.exists()):
                raise ParticipantBotError("Rename the local rpsdk module: submissions vendor the installed SDK.")
            if module.is_file():
                pending.append(module)
            elif (package / "__init__.py").is_file():
                pending.extend(path for path in package.rglob("*.py")
                               if "__pycache__" not in path.parts and not path.name.startswith("."))
    for name in ("README.md", "README.txt"):
        path = root / name
        if path.is_file():
            include(path)
    data = root / "data"
    if data.is_dir():
        for path in data.rglob("*"):
            if path.is_file():
                include(path)
    return sorted(collected.items())
