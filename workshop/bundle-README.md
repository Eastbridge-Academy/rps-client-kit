# Eastbridge RPS event kit

This folder contains everything for the two-hour RPS workshop: client kit 0.3.1,
its dependencies, four handout routes and a guide to the house bots. Facilitator
notes and reference bots are in a separate folder. The host will give you the
event's server URL, league slug and submit token.

## Set up your computer

Open **handouts/00-setup.pdf** first:

- Page 1: lab-machine setup and submission (all participants).
- Page 2: downloading and installing on macOS or Linux.
- Page 3: downloading and installing on Windows.
- Page 4: practice commands, scores and what gets uploaded.

The public [setup instructions](https://github.com/Eastbridge-Academy/rps-client-kit/blob/v0.3.1/README.md#on-your-own-laptop)
contain the same commands as selectable text. To get another copy of the kit,
[download the event ZIP](https://github.com/Eastbridge-Academy/rps-client-kit/releases/latest/download/rps-event-kit.zip).
No Git checkout or build is needed.

On a prepared lab machine, with Python 3.11+ and uv installed:

```bash
cd ~/rps-event-kit
sh ./start.sh "$HOME/rps-bot"
cd "$HOME/rps-bot"
source .venv/bin/activate
rps-cli test
rps-cli validate
```

On a personal laptop, install uv and Python as described in the setup handout
before running the platform's kit installation commands. The tools need an
internet connection for their initial download. After that, installation and
local play use the wheels in this folder; no compiler is needed. Submissions
and the dashboard need access to the event server.

You can rerun `start.sh` without losing bot.py or your tests. Use a separate
workshop project folder: setup installs the supplied kit into that folder's
.venv. Run bot commands from the project folder, not this event-kit folder.

## Choose your route

Print **00-setup.pdf in a separate pile**, then choose one level from 01 through
04. Every level begins with game theory and the bot API, followed by its own
exercises. Setup is not repeated in the level handouts.

| Packet | Suggested starting point | What you'll work on |
| --- | --- | --- |
| 01 Beginner, 5 pages | New to Python | Constant moves, cycles, Copycat and recognizing patterns |
| 02 Intermediate, 6 pages | Comfortable with lists, dictionaries and functions | Payoff estimates, windows, conditional behavior |
| 03 Advanced, 6 pages | Ready to build and test a statistical model | Markov models, order two, backoff and model tests |
| 04 Expert, 7 pages | Experienced with probability and algorithms | Expert weighting, regret assumptions, terminal utility |
| 05 House field guide, 2 pages | Any route; hints optional | All 16 personalities and experiments |

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
