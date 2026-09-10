#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<4"
# dependencies = ["httpx==0.28.1", "packaging==26.0"]
# ///
"""Build a portable offline bundle from the lockfile, wheel and rendered PDFs."""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import tomllib
from urllib.parse import urlparse
from zipfile import ZipFile, ZIP_DEFLATED

import httpx
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"


def run(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    wheel = ROOT / f"dist/eastbridge_rps_client_kit-{version}-py3-none-any.whl"
    if not wheel.is_file():
        raise RuntimeError("Build the kit with uv build first")
    pdfs = sorted((OUTPUT / "pdf").glob("*.pdf"))
    expected = {
        "00-setup.pdf", "01-beginner.pdf", "02-intermediate.pdf", "03-advanced.pdf",
        "04-expert.pdf", "05-house-bot-field-guide.pdf", "06-facilitator-notes.pdf",
    }
    if {pdf.name for pdf in pdfs} != expected:
        raise RuntimeError("Build and inspect the seven current workshop PDFs; remove stale PDFs from output/pdf")
    destination = OUTPUT / "rps-event-kit"
    # Only this generated directory is replaced; never participant projects.
    if destination.exists():
        shutil.rmtree(destination)
    wheels = destination / "wheelhouse"
    wheels.mkdir(parents=True)
    requirements = run("uv", "export", "--locked", "--no-default-groups", "--no-emit-project", "--no-hashes", "--no-header", "--no-annotate")
    packages = {(canonicalize_name(p["name"]), p["version"]): p for p in tomllib.loads((ROOT / "uv.lock").read_text())["package"]}
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        for line in requirements.splitlines():
            requirement = Requirement(line)
            pin = next(iter(requirement.specifier))
            if pin.operator != "==":
                raise RuntimeError(f"Unpinned dependency: {line}")
            package = packages[canonicalize_name(requirement.name), pin.version]
            candidates = [entry for entry in package.get("wheels", []) if entry["url"].endswith("-none-any.whl")]
            if not candidates:
                raise RuntimeError(f"No portable wheel for {line}; review platform support")
            entry = candidates[0]
            path = wheels / Path(urlparse(entry["url"]).path).name
            response = client.get(entry["url"])
            response.raise_for_status()
            path.write_bytes(response.content)
            if "sha256:" + digest(path) != entry["hash"]:
                raise RuntimeError(f"Wheel hash mismatch: {path.name}")
    shutil.copy2(wheel, wheels)
    (destination / "requirements.txt").write_text(f"eastbridge-rps-client-kit=={version}\n" + requirements + "\n")
    shutil.copy2(ROOT / "workshop/start.sh", destination / "start.sh")
    (destination / "start.sh").chmod(0o755)
    shutil.copy2(ROOT / "workshop/bundle-README.md", destination / "README.md")
    (destination / "handouts").mkdir()
    (destination / "facilitator").mkdir()
    for pdf in pdfs:
        folder = "facilitator" if pdf.name.startswith("06-") else "handouts"
        shutil.copy2(pdf, destination / folder / pdf.name)
    shutil.copytree(ROOT / "workshop/solutions", destination / "facilitator/solutions", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (destination / "reference").mkdir()
    shutil.copy2(ROOT / "README.md", destination / "reference/client-kit-README.md")
    shutil.copy2(ROOT / "workshop/verification.md", destination / "reference/verification.md")
    shutil.copy2(ROOT / "uv.lock", destination / "reference/uv.lock")
    if (ROOT / "LICENSE").is_file():
        shutil.copy2(ROOT / "LICENSE", destination / "reference/LICENSE")
    files = {str(path.relative_to(destination)): digest(path) for path in sorted(destination.rglob("*")) if path.is_file()}
    (destination / "BUILD.json").write_text(json.dumps({
        "version": version, "commit": run("git", "rev-parse", "HEAD"),
        "dirty": bool(run("git", "status", "--porcelain")), "files": files,
    }, indent=2) + "\n")
    files["BUILD.json"] = digest(destination / "BUILD.json")
    (destination / "SHA256SUMS").write_text("".join(f"{value}  {name}\n" for name, value in sorted(files.items())))
    archive = OUTPUT / "rps-event-kit.zip"
    with ZipFile(archive, "w", ZIP_DEFLATED) as bundle:
        for path in sorted(destination.rglob("*")):
            if path.is_file():
                bundle.write(path, path.relative_to(OUTPUT))
    print(f"{archive}: {archive.stat().st_size / 1024 / 1024:.1f} MiB; {len(list(wheels.glob('*.whl')))} portable wheels")
    print(f"SHA-256: {digest(archive)}")


if __name__ == "__main__":
    main()
