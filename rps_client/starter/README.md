# Your RPS bot

Run these commands from this folder, in the environment where you installed the kit.

1. `rps-cli test` checks that your bot handles an empty history and a full match.
2. `rps-cli validate` checks the contract and plays short smoke matches.
3. `rps-cli opponents` lists practice opponents; add `--hints` for suggestions.
4. `rps-cli play --against rocky,copycat --best-of 501 --seed 42 --games 3` practices across several seeds.
5. Edit `bot.py`, test again, and compare with a different seed.
6. Configure the server, league and token using the values from your facilitator:
   `rps-cli config set api_url https://arena.eastbrid.ge`,
   `rps-cli config set league rps`, and `rps-cli config set token TOKEN`.
7. `rps-cli doctor` checks your environment and server connection.
8. `rps-cli submit "Team Name"` uploads a version; `rps-cli status "Team Name"` checks whether it is active.

Use the same team name every time. Uploading is followed by server validation;
editing this file alone does not update your tournament bot.

Configuration lives in `.rps-cli.json` in this folder. Keep the token out of Git.
Your Python helper modules/packages and files under `data/` are packaged on submission.
Use the Python standard library and `rpsdk`; your local virtual environment is not uploaded.

The series has exactly `best_of` throws, including draws. `match_state["round"]`
is zero-based. `last_outcome` is your previous throw's result, or None initially.
Both histories reset between matches and never contain the current unseen throw.

Tests check correctness, not playing strength. Local practice has a whole-match
time limit; the arena additionally enforces per-throw limits. Do not use sleeps,
network calls or large training jobs in your bot.
