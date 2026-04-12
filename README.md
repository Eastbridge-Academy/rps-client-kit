Eastbridge RPS Client Kit
=========================

This repository contains the student-facing tooling for the Eastbridge Rock-Paper-Scissors tournament:

- `rps-cli` for starter setup, local validation, play, submission, and status
- `rpsdk` with the shared `Move` enum used by participant bots
- `rps_house_bots` with the bundled local opponents used by the simulator

Install
-------

Recommended with `uv`:

```bash
uv tool install git+https://github.com/Eastbridge-Academy/rps-client-kit
```

Or with `pipx`:

```bash
pipx install git+https://github.com/Eastbridge-Academy/rps-client-kit
```

If you already cloned this repository:

```bash
uv sync
uv run rps-cli --help
```

Configure
---------

Point the CLI at the tournament server and set the shared submit token:

```bash
rps-cli config set api_url https://rps.eastbrid.ge
rps-cli config set token <SUBMIT_TOKEN>
```

Or use environment variables:

```bash
export RPS_API_URL=https://rps.eastbrid.ge
export RPS_SUBMIT_TOKEN=<SUBMIT_TOKEN>
```

Quickstart
----------

Start a new bot project:

```bash
rps-cli init my-bot
cd my-bot
```

Run a local contract check and short smoke match from a folder containing `bot.py`:

```bash
rps-cli validate
rps-cli validate --against rocky,copycat --best-of 9
```

Run longer local simulations:

```bash
rps-cli play
rps-cli play --against rocky,copycat
```

Submit a bot:

```bash
rps-cli submit "Team Name" --email you@example.com
```

The CLI sends the shared token as `X-Submit-Token`.

Check your latest submission state with:

```bash
rps-cli status "Team Name"
```

`status` shows the currently active tournament version, your latest submitted version, and any rejection reason returned by validation.

Bot Contract
------------

Participant bots should expose:

```python
from rpsdk import Move

def next_move(my_history: list[Move], opponent_history: list[Move], match_state: dict) -> Move:
    ...
```

Optional:

```python
def setup(config: dict) -> None:
    ...
```

Current `match_state` keys:

- `round`
- `best_of`
- `seed`
- `opponent_last_outcome`
- `timeouts`
- `opponent_timeouts`

Current local validation checks:

- `bot.py` imports successfully
- `setup(config)` is optional but must be callable if present
- `next_move(...)` must be callable and return `rock`, `paper`, or `scissors`
- `validate` then runs a short local smoke series against bundled house bots

Bundled House Bots
------------------

- `contrarian`
- `copycat`
- `cycle_counter`
- `cycle_rps`
- `random_uniform`
- `rocky`
- `switcheroo`
- `win_stay_lose_shift`

Release Workflow
----------------

Tags like `v0.1.2` trigger a GitHub Actions release build that uploads a wheel and source distribution to GitHub Releases.
