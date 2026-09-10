# Running the workshop

Plan to have everyone's starter bot in the arena during the first 20 minutes. Participants can then work through whichever route suits them. All four packets include the same setup and mechanics pages, so people can start anywhere and switch during the session.

## Before participants arrive

Put an extracted **rps-event-kit** folder in each lab account's home directory. Try start.sh on the Raspberry Pi image participants will use, with Python 3.11+ and uv installed. Setup and local practice work offline. Check the event network as well, since submissions and the dashboard need it.

Have the event's server URL, active RPS league slug and submit token ready to distribute. Participants will substitute these for the examples in the handouts. Confirm which server will host the event and test a submission from the supplied kit; the dev rehearsal may be running on a different server.

Print a few copies of each route, with more copies of whichever levels you expect to need. Offer the two-page house-bot guide as hints. Some participants may prefer to work out the bots' rules themselves.

## Suggested schedule

| Minutes | What happens |
| --- | --- |
| 0-10 | Demonstrate a match and the difference between a throw, match and league round. |
| 10-20 | Initialize, test and submit the random starter; confirm an active version. |
| 20-45 | First route exercise and a small local comparison. |
| 45-75 | Add one model or improvement; circulate and debug histories. |
| 75-95 | Try other house bots and compare notes in pairs. |
| 95-110 | Save a final version and test it on fresh seeds. |
| 110-120 | Submit, confirm activation, watch results and share one finding. |

Spend the opening part of the session helping people get set up. Pairing newcomers with someone who can read a traceback can help, if both people would like that. Let participants finish the exercise they're working on even if others have moved ahead.

> **Opening demonstration:** show constant rock losing to paper, then show a balanced repeating cycle being exploited. Ask whether "one third of each move" was enough to make the second bot unpredictable. Follow with the independent-uniform baseline and its expected zero net payoff.
---page---
# Testing the lab setup

The event ZIP contains the kit, its dependencies and the printable handouts. Run through the setup from that ZIP before copying it to the lab accounts. This checks that participants have everything they'll need, including for offline practice.

## Try a participant project

On the same image participants will use:

```bash
cd ~/rps-event-kit
./start.sh ~/rps-smoke
cd ~/rps-smoke
source .venv/bin/activate
rps-cli --version
rps-cli test
rps-cli validate
rps-cli play --against rocky,sticky,double_take --best-of 501
rps-cli package --output smoke.zip
```

Set the event URL, league and token with `config set`, then run `doctor`. Submit a test bot, wait for its version to become active, and inspect a completed match. Afterwards, remove that test entry through the organizer controls if it won't be playing in the event.

The doctor checks the connection and active RPS league; submission also checks the token. Distribute the token separately from these handouts and keep it out of source control. Each participant should use their own project folder, where `.rps-cli.json` stores their settings.

## Troubleshooting

| Symptom | First check |
| --- | --- |
| rps-cli not found | Return to the project and activate .venv. |
| Move import fails in the editor | Select the project's .venv interpreter; run the CLI from that environment. |
| IndexError on the first throw | Guard empty history before [-1], and two entries before [-2]. |
| Works first match, fails later | Reset globals in setup; avoid counting all old transitions again. |
| No active RPS league | Check the server URL and league slug with doctor. |
| Upload queued or rejected | Read status; it reports both active and latest versions. |
| Local success, server failure | Check startup and move times, then any imports beyond the standard library and SDK. |
| Wrong bot on the scoreboard | Reuse the exact team name and verify the displayed active version. |

Local practice limits the total match time; the arena also limits each move. A bot can pass locally and still take too long on one server call. If that happens, time its startup and individual moves to find the slow part.

---page---
# Hints, answers and discussion

The house guide describes the bots included in the kit. Its route labels show where each bot appears in the exercises. Matchups will often cut across those levels: a simple strategy can beat a complicated one that predicts it poorly.

## Answers to the exercises

- **Rocky:** paper wins every throw. Against Cycle RPS, predict the next item, then counter it; countering the previous item is late.
- **Copycat:** its next move is your last move. **Echo Two:** use your move two turns ago. Guard the first one or two calls respectively.
- **Contrarian:** predict its counter to your last move, then counter that prediction.
- **Sticky:** counter its previous move. Its conditional repeat probability is 0.8 even though long-run single-move frequencies are balanced.
- **Win Stay Lose Shift:** after its win or draw, counter its last move. After its loss, play the move its last move beats; this wins against one possible switch and draws against the other.
- **40/21/39 distribution:** rock earns +0.18, paper +0.01 and scissors -0.19. Rock wins against the plentiful scissors and loses only to the relatively scarce paper.
- **Double Take:** its cyclic adjacent pairs are RR, RP, PR, RS, SP, PP, PS, SS and SR. Each identifies one deterministic successor. Single-move conditional rows are balanced over complete cycles.

## Questions for more experienced participants

To check prediction timing, ask participants to change a later item in a written sequence. Earlier predictions should stay the same. The saved prediction must be scored before the model learns from the newly observed throw.

For a portfolio, compare each expert's virtual gains with its score in a match played alone. Against an adaptive opponent, its own past moves can change the opposition it faces. If a participant adds discounting, ask where the undiscounted regret proof would need to change.

For the end-of-match example, use $q$ = 30% rock, 60% paper, 10% scissors. Scissors has expected payoff $+0.30$ per throw and paper has $+0.20$. With one throw left and a one-point lead, paper earns expected match points $0.95$, while scissors earns $0.85$. Ask participants to calculate the choices when they're one point behind.

## Closing discussion

Ask participants to show a match or experiment that surprised them. Have them explain what their bot was predicting and whether they changed it afterwards. Return to the opening random-play example: which opponents had a habit they could learn, and what happened against Random Uniform?

The source repository includes reference bots and tests for the exercises. You can share them for participants to inspect, modify or compare with their own work. The README beside them explains how to run each one.
