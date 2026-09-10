The RPS kit for the two-hour Eastbridge workshop, with 16 house bots and four
handout routes for Python beginners through experienced programmers.

## Install on your laptop

Follow the [Windows, macOS or Linux setup instructions](https://github.com/Eastbridge-Academy/rps-client-kit/blob/v0.3.0/README.md#on-your-own-laptop).
They use uv and the wheel attached below, with no Git or compiler required.

The same tagged-Git install used by the chess kit also works:

```bash
uv tool install --python 3.12 git+https://github.com/Eastbridge-Academy/rps-client-kit@v0.3.0
uv tool update-shell
```

Open a new terminal, create a folder for your bot, and run `rps-cli init`,
`rps-cli test` and `rps-cli play --against rocky,copycat`. The host supplies
the event URL, league slug and submit token.

## Downloads

- **rps-event-kit.zip**: the complete offline kit, dependency wheels, all
  handouts, setup script and facilitator reference bots. Lab machines need
  Python 3.11+ and uv installed before using its offline setup.
- **eastbridge_rps_client_kit-0.3.0-py3-none-any.whl**: installable Python package.
- **01 through 04 PDFs**: beginner, intermediate, advanced and expert packets.
  Pick one; each includes the same setup and mechanics pages.
- **05-house-bot-field-guide.pdf**: all 16 house bots with explanations and hints.
- **06-facilitator-notes.pdf**: session schedule, setup checks and worked answers.
- **Source archive**: the kit, workshop text, LaTeX style and Academy logo.

## Changes since 0.1

Project-local settings, scaffolded tests, validation and submission status,
practice over multiple seeds with complete throw exports, and helper-module
packaging. Submissions carry the SDK version used during local testing.
The expanded house field includes Echo Two, Sticky and Double Take.

Existing participants should configure the server, league and token in each
bot folder. The current `last_outcome` field reports the preceding throw from
your bot's perspective; the matching Arena worker update is required. The
earlier cumulative-score field has been removed.
