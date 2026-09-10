# Eastbridge RPS Client Kit

Build a Python rock-paper-scissors bot, practice against a varied house field,
and submit versions to the Eastbridge Arena. Python 3.11+; Raspberry Pi 5,
Linux and macOS are supported. The participant workflow mirrors the chess kit:
initialize a project, test it, play locally, submit, then check validation status.

## Start at the event

The facilitator supplies `rps-event-kit.zip` with this release's wheel, dependency
wheels, printable handouts and a setup script. Extract it to `~/rps-event-kit`:

```bash
cd ~/rps-event-kit
./start.sh ~/rps-bot
cd ~/rps-bot
source .venv/bin/activate
rps-cli test
rps-cli validate
rps-cli opponents
rps-cli play --against rocky,copycat --best-of 501 --seed 42 --games 3
```

The starter already plays a legal random strategy. Edit `bot.py` and run the
checks again. The four handout routes share the same setup; switch routes freely.

`start.sh` requires `uv` and Python 3.11+ and installs from the supplied wheels
without querying a package index. Facilitators should prepare and test the lab
before the workshop. A fresh terminal needs `source .venv/bin/activate` again.

## Install from a checkout or wheel

For development in this repository:

```bash
uv sync
uv run rps-cli --help
uv run pytest
```

For a new participant project with a supplied release wheel:

```bash
mkdir my-bot
cd my-bot
uv venv
source .venv/bin/activate
uv pip install /path/to/eastbridge_rps_client_kit-0.3.0-py3-none-any.whl
rps-cli init
rps-cli test
```

The source repository is https://github.com/Eastbridge-Academy/rps-client-kit.
Do not use a guessed release tag: an unpushed local release is available through
its event bundle until the organizer publishes it.

## Configure and enter the tournament

Use the server, active league slug and token supplied by the facilitator:

```bash
rps-cli config set api_url https://arena.eastbrid.ge
rps-cli config set league rps
rps-cli config set token TOKEN
rps-cli doctor
rps-cli submit "Team Name"
rps-cli status "Team Name"
```

`TOKEN` is a placeholder; the event token is not embedded in the kit or handouts.
The league name above is an example, not automatic league discovery. For the dev
rehearsal use `https://dev.arena.eastbrid.ge` and `rps-rehearsal`.

Settings live in **the current project's `.rps-cli.json`**, like the chess kit.
Run commands from the bot folder. `RPS_API_URL`, `RPS_LEAGUE` and
`RPS_SUBMIT_TOKEN` override the project file. Environment overrides are not
persisted when a different setting is saved. `info` and `config get token` mask
secrets; the scaffold adds the config file to `.gitignore`.

Reuse the same team name on every submission. Uploading creates a version that
must pass server validation. `status` shows both the active version and latest
submission, including rejection reasons. A rejected replacement does not replace
your previously active version. Editing local code alone never changes the arena.

## Practice and investigate

```bash
rps-cli opponents --hints
rps-cli play --against sticky,double_take --best-of 501 --games 5 --seed 100
rps-cli play --against copycat --output throws.json
rps-cli test -q
rps-cli test -k first_throw
rps-cli validate --against rocky,copycat --best-of 9
rps-cli validate --no-smoke
rps-cli info
```

`--games 5 --seed 100` uses seeds 100 through 104 for each opponent. Every match
starts fresh, including helper-module globals and RNG state. `--output` saves
all observed throws, seeds, scores and errors in JSON. Compare seeds reserved for
testing, not just the ones used to tune your bot. Local practice reports match
wins and throw W-L-D separately; it does not calculate tournament Elo.

Practice defaults to a 30-second whole-match deadline; use `--timeout` for a
longer local run. This is not the arena's per-throw enforcement. Local validation
runs imports, setup and three history-aware calls in a bounded subprocess, then
optional smoke matches. Both commands report bot errors with a nonzero exit code.

## Bot contract

```python
from rpsdk import Move

def setup(config: dict) -> None:  # optional, once per match
    ...

def next_move(my_history: list[Move], opponent_history: list[Move],
              match_state: dict) -> Move:
    return Move.PAPER
```

- The histories contain completed throws, oldest first. They are empty initially.
- Both players choose without seeing the current opposing throw.
- `setup` receives your bot's seed. The histories and process state reset for each match.
- Return `Move.ROCK`, `Move.PAPER` or `Move.SCISSORS`; their lowercase strings also work.
- `Move.from_value` normalizes a move, and `my_move.beats(other_move)` tests a win.
- The arena runs exactly `best_of` throws, including draws. It does not stop when
  someone reaches a majority. A 501-throw series can still end with equal scores.

`match_state` contains:

| Key | Meaning |
| --- | --- |
| `round` | Zero-based throw index: 0 through `best_of - 1`. |
| `best_of` | Fixed series length, currently 501 for the rehearsal. |
| `seed` | Your bot's reproducibility seed, not the opponent's seed. |
| `last_outcome` | Your last throw's `win`, `loss` or `draw`; `None` initially. |
| `timeouts` | Your accumulated server timeouts in this match. |
| `opponent_timeouts` | The opponent's accumulated server timeouts. |

Use the standard library and `rpsdk`. Submissions vendor the installed SDK;
other locally installed packages are not automatically shipped. Source helpers
and `data/` files are packaged, but the virtual environment and project config
are not. Data file paths should be relative to `Path(__file__).parent`.

The runtime isolates bot processes but is not a security boundary. Treat bot
code as trusted workshop code. Keep imports and moves quick; do not use network
calls, sleeps or large training jobs during a match.

## 0.3 participant-workflow changes

Configuration is project-local instead of home-global. Run the three config
commands in each project; there is no silent migration of a shared token.
The misleading `opponent_last_outcome` cumulative-score field is replaced by
`last_outcome`, which describes the actual preceding throw from your perspective.
The corresponding Arena worker update is required when deploying this kit.

`init` preserves existing files unless `--force` is explicit. It also fills in
missing tests and the README, so existing bot folders can adopt the new workflow.

## Releases

The [two-hour workshop](workshop/README.md) includes four printable routes,
the house-bot field guide, facilitator reference bots, and offline bundle builds.
Choose a route directly; each repeats the same setup and mechanics foundations.

For a local development server that uses a private CA, Python may not trust the
certificate even when the browser does. Set `SSL_CERT_FILE` to the facilitator's
trusted CA PEM file. This applies to doctor, submit and status; production should
use its normal publicly trusted certificate. No certificate bypass is required.

Tags trigger the repository's GitHub Actions wheel/source release build. The
organizer reviews and publishes a tested tag; local build scripts also produce
an event bundle so the workshop can use the exact reviewed version offline.
