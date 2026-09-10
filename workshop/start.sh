#!/bin/sh
# Participant setup: uses local wheels and already-installed Python + uv.
set -eu

if [ "$#" -gt 1 ]; then
    printf '%s\n' 'Usage: ./start.sh [project-directory]' >&2
    exit 2
fi
if ! command -v uv >/dev/null 2>&1; then
    printf '%s\n' 'uv is missing. Ask the facilitator to finish the lab setup.' >&2
    exit 1
fi
RPS_BUNDLE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
RPS_TARGET=${1:-"$HOME/rps-bot"}
mkdir -p -- "$RPS_TARGET"
RPS_TARGET=$(CDPATH= cd -- "$RPS_TARGET" && pwd)
export UV_PYTHON_DOWNLOADS=never
export UV_OFFLINE=1

if [ ! -x "$RPS_TARGET/.venv/bin/python" ]; then
    uv venv --python '>=3.11' "$RPS_TARGET/.venv"
fi
"$RPS_TARGET/.venv/bin/python" -c 'import sys; assert (3, 11) <= sys.version_info < (4, 0), "Python 3.11+ is required"'
uv pip install --python "$RPS_TARGET/.venv/bin/python" --no-index \
    --find-links "$RPS_BUNDLE_DIR/wheelhouse" \
    --requirement "$RPS_BUNDLE_DIR/requirements.txt"
cd -- "$RPS_TARGET"
"$RPS_TARGET/.venv/bin/rps-cli" init
printf '\nProject ready in %s\n' "$RPS_TARGET"
printf '%s\n' 'Open a terminal in that folder, then run:' \
    '  source .venv/bin/activate' '  rps-cli test' '  rps-cli validate'
