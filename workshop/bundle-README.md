# Eastbridge RPS event kit

A two-hour workshop for Python newcomers through domain experts. This bundle
contains client kit 0.3.0, pinned dependency wheels, four printable routes, a
house-bot field guide, and separate facilitator material. No event token is
included. Obtain the server URL, active RPS league slug and token from the host.

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
Paths containing spaces are supported when quoted. Rerunning setup preserves
bot.py and existing tests. It installs the pinned kit into the chosen .venv;
use a dedicated workshop project rather than another application's environment.

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

| Packet | Suggested starting point | Main investigation |
| --- | --- | --- |
| 01 Beginner, 7 pages | New to Python or ready for concrete patterns | Constants, cycles, mimics, evidence checks |
| 02 Intermediate, 8 pages | Comfortable with lists, dictionaries and functions | Payoff estimates, windows, conditional behavior |
| 03 Advanced, 8 pages | Ready to build and test a statistical model | Markov context, order two, backoff, honest evaluation |
| 04 Expert, 9 pages | Experienced with probability and algorithms | Expert weighting, regret assumptions, terminal utility |
| 05 House field guide, 2 landscape pages | Any route; hints optional | All 16 personalities and experiments |

Facilitator notes and complete reference bots are in facilitator/. They can be
shared as optional comparisons after participants have explored their own ideas.
The kit README in reference/ explains all CLI commands and the submission format.

## Enter the actual event

From the participant project, with its environment active:

```bash
rps-cli config set api_url https://arena.eastbrid.ge
rps-cli config set league rps
rps-cli config set token TOKEN
rps-cli doctor
rps-cli submit "Your Team Name"
rps-cli status "Your Team Name"
```

Replace all three settings with the host's actual values. `TOKEN` is a placeholder.
Use the same team name for later versions. Saving a file alone does not submit it.
The doctor checks the active league and server, but submission authenticates the
token. A queued upload becomes eligible only after server validation succeeds.

## Provenance and verification

`BUILD.json` records the source commit, whether it was dirty, kit version and
every file's SHA-256. `SHA256SUMS` is also included for tools such as sha256sum.
Dependency wheels are fetched from the exact URLs and hashes in uv.lock.
This is a local review bundle, not evidence that a public release or production
deployment has occurred. The organizer must choose and smoke-test the event server.
