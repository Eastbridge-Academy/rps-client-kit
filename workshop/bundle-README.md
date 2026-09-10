# Eastbridge RPS event kit

This folder contains everything for the two-hour RPS workshop: client kit 0.3.0,
its dependencies, four handout routes and a guide to the house bots. Facilitator
notes and reference bots are in a separate folder. The host will give you the
event's server URL, league slug and submit token.

## Raspberry Pi / Linux / macOS

The lab needs **Python 3.11 or newer and uv installed before the session**.
Extract this ZIP into your home folder; it creates `rps-event-kit/`. Then:

```bash
cd ~/rps-event-kit
./start.sh ~/rps-bot
cd ~/rps-bot
source .venv/bin/activate
rps-cli test
rps-cli validate
```

If an extractor removes executable permissions, use `sh ./start.sh ~/rps-bot`.
Put quotes around paths that contain spaces. You can rerun setup without losing
bot.py or your existing tests. Use a separate workshop project folder: setup
installs the supplied kit into that folder's .venv.

Installation and local play use **no network**. Setup will not download Python.
If uv cannot find Python 3.11+, ask the host to install it before trying again.
The universal Python wheels work on ARM64 and x86; no compiler is needed.
Submissions, status and the live dashboard need access to the event server.

## Windows PowerShell alternative

With Python 3.11+ and uv installed, open PowerShell inside rps-event-kit:

```powershell
uv venv --offline --no-python-downloads --python ">=3.11" ..\rps-bot\.venv
uv pip install --offline --no-index --python ..\rps-bot\.venv\Scripts\python.exe --find-links .\wheelhouse -r .\requirements.txt
cd ..\rps-bot
.\.venv\Scripts\rps-cli.exe init
.\.venv\Scripts\rps-cli.exe test
```

Use the explicit executable path if activation is blocked by a local policy.
The Windows commands are provided for personal machines; the event's primary
lab path is Linux. See the verification report for platforms actually exercised.

## Choose your route

Print **one** PDF from handouts/01 through 04. Each already includes the same
four-page foundations; you do not need to print common pages separately.

| Packet | Suggested starting point | What you'll work on |
| --- | --- | --- |
| 01 Beginner, 7 pages | New to Python | Constant moves, cycles, Copycat and recognizing patterns |
| 02 Intermediate, 8 pages | Comfortable with lists, dictionaries and functions | Payoff estimates, windows, conditional behavior |
| 03 Advanced, 8 pages | Ready to build and test a statistical model | Markov models, order two, backoff and model tests |
| 04 Expert, 9 pages | Experienced with probability and algorithms | Expert weighting, regret assumptions, terminal utility |
| 05 House field guide, 2 landscape pages | Any route; hints optional | All 16 personalities and experiments |

Facilitator notes and complete reference bots are in facilitator/. They can be
shared as optional comparisons after participants have explored their own ideas.
The kit README in reference/ explains all CLI commands and the submission format.

## Join the event

From the participant project, with its environment active:

```bash
rps-cli config set api_url https://arena.eastbrid.ge
rps-cli config set league rps
rps-cli config set token TOKEN
rps-cli doctor
rps-cli submit "Your Team Name"
rps-cli status "Your Team Name"
```

Substitute the host's values for the three settings, including `TOKEN`. Reuse
the same team name for later versions, and run `submit` whenever you want the
arena to use your edits. The doctor checks the connection and league;
submission also checks the token. Use `status` to see when the uploaded version
has passed validation and become active.

## Provenance and verification

`BUILD.json` records the source commit, whether it was dirty, kit version and
every file's SHA-256. `SHA256SUMS` is also included for tools such as sha256sum.
Dependency wheels are fetched from the exact URLs and hashes in uv.lock.
The report in reference/verification.md lists the checks run on this kit and
the remaining checks for the organizer to run on the lab machines and event server.
