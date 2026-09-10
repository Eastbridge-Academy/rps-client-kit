#!/bin/sh
# Run in a disposable directory, preferably with network access disabled.
set -eu
RPS_BUNDLE=$(CDPATH= cd -- "$1" && pwd)
RPS_TEST_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/rps-bundle-smoke.XXXXXX")
RPS_PROJECT="$RPS_TEST_ROOT/project with spaces"
sh "$RPS_BUNDLE/start.sh" "$RPS_PROJECT"
cd -- "$RPS_PROJECT"
RPS_CLI="$RPS_PROJECT/.venv/bin/rps-cli"
"$RPS_CLI" --version
"$RPS_CLI" info
"$RPS_CLI" test
"$RPS_CLI" validate
"$RPS_CLI" opponents --hints
"$RPS_CLI" play --against rocky,sticky,double_take --best-of 501 --output smoke.json
"$RPS_CLI" package --output submission.zip
"$RPS_PROJECT/.venv/bin/python" - "$RPS_BUNDLE" <<'PY'
from hashlib import sha256
import json
from pathlib import Path
import sys
from zipfile import ZipFile
bundle = Path(sys.argv[1])
manifest = json.loads((bundle / "BUILD.json").read_text())
for name, expected in manifest["files"].items():
    assert sha256((bundle / name).read_bytes()).hexdigest() == expected, name
with ZipFile("submission.zip") as archive:
    assert "bot.py" in archive.namelist()
    assert "rpsdk/__init__.py" in archive.namelist()
    assert not any(".venv" in name or ".rps-cli.json" in name for name in archive.namelist())
    archive.extractall("unpacked")
data = json.loads(Path("smoke.json").read_text())
assert len(data["matches"]) == 3
assert all(len(match["rounds"]) == 501 and match["errors"] == 0 for match in data["matches"])
Path("bot.py").write_text(Path("bot.py").read_text() + "\n# preserved participant edit\n")
Path("original-bot.txt").write_bytes(Path("bot.py").read_bytes())
print("Bundle checksums, archive contents and 1,503 recorded throws verified")
PY
"$RPS_CLI" validate unpacked/bot.py
sh "$RPS_BUNDLE/start.sh" "$RPS_PROJECT"
cmp bot.py original-bot.txt
"$RPS_CLI" play --bot "$RPS_BUNDLE/facilitator/solutions/advanced.py" \
    --against double_take --best-of 501
"$RPS_CLI" package --bot "$RPS_BUNDLE/facilitator/solutions/advanced.py" --output advanced.zip
printf '\nOffline bundle smoke passed; artifacts: %s\n' "$RPS_TEST_ROOT"
