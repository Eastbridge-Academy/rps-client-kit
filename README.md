# Eastbridge RPS Client Kit

Write a Python rock-paper-scissors bot, practice against the house bots, and
enter it in the Eastbridge Arena. The kit works on Windows, macOS and Linux,
including Raspberry Pi 5. It requires Python 3.11 or newer; the setup below
uses Python 3.12.

**[Download v0.3.0](https://github.com/Eastbridge-Academy/rps-client-kit/releases/tag/v0.3.0)**
for the installable wheel, printable handouts and complete event ZIP.

## On your own laptop

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then open
a new terminal. uv will download Python 3.12 if you don't already have it.
The wheel installs directly from GitHub; you don't need Git or a compiler.

**macOS or Linux:**

```bash
mkdir rps-bot
cd rps-bot
uv venv --python 3.12
uv pip install --python .venv/bin/python https://github.com/Eastbridge-Academy/rps-client-kit/releases/download/v0.3.0/eastbridge_rps_client_kit-0.3.0-py3-none-any.whl
source .venv/bin/activate
rps-cli init
rps-cli test
rps-cli play --against rocky,copycat --best-of 501
```

**Windows PowerShell:**

```powershell
mkdir rps-bot
cd rps-bot
uv venv --python 3.12
uv pip install --python .venv\Scripts\python.exe https://github.com/Eastbridge-Academy/rps-client-kit/releases/download/v0.3.0/eastbridge_rps_client_kit-0.3.0-py3-none-any.whl
.\.venv\Scripts\rps-cli.exe init
.\.venv\Scripts\rps-cli.exe test
.\.venv\Scripts\rps-cli.exe play --against rocky,copycat --best-of 501
```

Edit `bot.py` and rerun the tests. In your editor, select this project's `.venv`
Python interpreter so it can find `rpsdk`. On Windows, use
`.\.venv\Scripts\rps-cli.exe` wherever the handouts say `rps-cli`; this works
without changing PowerShell's script execution policy. On macOS and Linux,
activate `.venv` again whenever you open a new terminal.

If you already use the chess kit as a uv tool, the same installation method
works here. This option requires Git:

```bash
uv tool install --python 3.12 git+https://github.com/Eastbridge-Academy/rps-client-kit@v0.3.0
uv tool update-shell
```

Open a new terminal, create a bot folder, then run `rps-cli init` there. The
tool runs tests and bots in its own Python environment. The project setup above
also makes the SDK available to your editor and to Python scripts in `.venv`.

## Start at the event

Download [rps-event-kit.zip](https://github.com/Eastbridge-Academy/rps-client-kit/releases/download/v0.3.0/rps-event-kit.zip),
or use the copy supplied by the facilitator. It includes the kit, dependency
wheels, handouts and an offline setup script. Extract it to `~/rps-event-kit`:

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

You can also install the tagged source into a project with
`uv pip install git+https://github.com/Eastbridge-Academy/rps-client-kit@v0.3.0`.
This requires Git; the wheel instructions above use the same kit version.

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

Choose a handout for your programming experience. Each includes the same four
pages of setup, mechanics and strategy fundamentals:

- [Beginner: Find a pattern](https://github.com/Eastbridge-Academy/rps-client-kit/releases/download/v0.3.0/01-beginner.pdf) (7 pages)
- [Intermediate: Count the moves](https://github.com/Eastbridge-Academy/rps-client-kit/releases/download/v0.3.0/02-intermediate.pdf) (8 pages)
- [Advanced: Markov models](https://github.com/Eastbridge-Academy/rps-client-kit/releases/download/v0.3.0/03-advanced.pdf) (8 pages)
- [Expert: Combine several strategies](https://github.com/Eastbridge-Academy/rps-client-kit/releases/download/v0.3.0/04-expert.pdf) (9 pages)
- [House-bot field guide](https://github.com/Eastbridge-Academy/rps-client-kit/releases/download/v0.3.0/05-house-bot-field-guide.pdf) (2 landscape pages)
- [Facilitator notes](https://github.com/Eastbridge-Academy/rps-client-kit/releases/download/v0.3.0/06-facilitator-notes.pdf) (3 pages)

The [workshop source](workshop/README.md) includes the reference bots and build
instructions. The event ZIP contains all these PDFs and the reference bots.

For a local development server that uses a private CA, Python may not trust the
certificate even when the browser does. Set `SSL_CERT_FILE` to the facilitator's
trusted CA PEM file. This applies to doctor, submit and status; production should
use its normal publicly trusted certificate. No certificate bypass is required.

Tags trigger the repository's GitHub Actions wheel/source release build. The
organizer reviews and publishes a tested tag; local build scripts also produce
an event bundle so the workshop can use the exact reviewed version offline.
