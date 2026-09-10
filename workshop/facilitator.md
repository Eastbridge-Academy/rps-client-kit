# Run the room

This is a two-hour public event, not a shortened three-month chess course. Get a legal bot into the arena early, then give participants room to explore at a comfortable level. The four packages share the same mechanics and installation pages; nobody needs to complete an earlier route before choosing a later one.

## Before participants arrive

Give each lab account an extracted **rps-event-kit** folder in its home directory. Test the included start.sh with the actual Raspberry Pi OS image, Python 3.11+ and uv. The wheelhouse supports offline package installation; local practice is offline too. Live submissions and the dashboard still need the event network and arena.

Prepare the event's server URL, active RPS league slug and submit token. The printed `rps` slug and `TOKEN` are examples, not embedded credentials. Confirm the intended server is deployed with the matching kit/worker contract before distributing a token. The currently running dev rehearsal is not automatically the public event.

Print one selected route per participant, plus the two-page house-bot field guide if you want hints available. Start with a few copies of each route and let people switch. Keep the field guide optional for participants who want to infer personalities without reading their rules.

## A workable schedule

| Minutes | What happens |
| --- | --- |
| 0-10 | Demonstrate a match and the difference between a throw, match and league round. |
| 10-20 | Initialize, test and submit the random starter; confirm an active version. |
| 20-45 | First route exercise and a small local comparison. |
| 45-75 | Add one model or improvement; circulate and debug histories. |
| 75-95 | Cross-test against other house personalities; compare notes in pairs. |
| 95-110 | Freeze a candidate and test on fresh seeds. |
| 110-120 | Submit, confirm activation, watch results and share one finding. |

Offer help with setup before discussing strategy. Pair a Python newcomer with someone comfortable reading tracebacks if both are happy with that arrangement. A participant who only builds a reliable Rocky counter can still explain a prediction and a response; they need not rush into a Markov model.

> **Opening demonstration:** show constant rock losing to paper, then show a balanced repeating cycle being exploited. Ask whether "one third of each move" was enough to make the second bot unpredictable. Follow with the independent-uniform baseline and its expected zero net payoff.
---page---
# Check the event path

The kit, handouts and bundle have separate jobs. The wheel supplies the CLI and SDK. The PDFs guide the workshop. The bundle pins the reviewed wheel and its dependencies so a package-index outage does not consume the session.

## Lab smoke run

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

Use the actual event settings with `config set`, then run `doctor`. Complete one designated smoke submission before opening the event, verify that its version becomes active, and inspect a finished match. Use the organizer controls to remove that designated smoke bot if it should not enter the field.

The doctor checks reachability and the active RPS league; a configured token is not authenticated until submission. Keep the submit token out of printed packets and source control. Participants should work in their own project folders because `.rps-cli.json` is project-local.

## Common interruptions

| Symptom | First check |
| --- | --- |
| rps-cli not found | Return to the project and activate .venv. |
| Move import fails in the editor | Select the project's .venv interpreter; run the CLI from that environment. |
| IndexError on the first throw | Guard empty history before [-1], and two entries before [-2]. |
| Works first match, fails later | Reset globals in setup; avoid counting all old transitions again. |
| No active RPS league | Check server and slug with doctor; do not guess a flat API route. |
| Upload queued or rejected | Read status; it reports both active and latest versions. |
| Local success, server failure | Check startup/per-throw cost and imported dependencies; the whole venv is not shipped. |
| Wrong bot on the scoreboard | Reuse the exact team name and verify the displayed active version. |

Local practice has a whole-match deadline, while the arena enforces move budgets. A bot can finish within the local total limit while one individual server call is too slow. Keep the standard-library examples small and run the designated server smoke check.

---page---
# Hints, answers and discussion

The house guide is generated from the kit's catalogue so the descriptions agree with the shipped personalities. Suggested routes are teaching groupings, not a total ordering of competitive strength. A specialized weak bot can expose a sophisticated bot's assumption.

## Small answers worth checking by hand

- **Rocky:** paper wins every throw. Against Cycle RPS, predict the next item, then counter it; countering the previous item is late.
- **Copycat:** its next move is your last move. **Echo Two:** use your move two turns ago. Guard the first one or two calls respectively.
- **Contrarian:** predict its counter to your last move, then counter that prediction.
- **Sticky:** counter its previous move. Its conditional repeat probability is 0.8 even though long-run single-move frequencies are balanced.
- **Win Stay Lose Shift:** after its win or draw, counter its last move. After its loss, play the move its last move beats; this wins against one possible switch and draws against the other.
- **40/21/39 distribution:** rock earns +0.18, paper +0.01 and scissors -0.19. A reply to the most frequent move is not automatically the best payoff response.
- **Double Take:** its cyclic adjacent pairs are RR, RP, PR, RS, SP, PP, PS, SS and SR. Each identifies one deterministic successor. Single-move conditional rows are balanced over complete cycles.

## Questions for more experienced participants

A stored prediction must be evaluated before it learns the newly observed throw. Ask them to change a future item in a written sequence and show that earlier predictions stay unchanged.

For a portfolio, distinguish virtual one-step gains on the actual history from the outcomes of experts that play their own complete matches. Adaptive opponents make those different counterfactuals. Discounting may help with changing behavior, but it changes the regret analysis.

For a terminal-objective example, use q = 30% rock, 60% paper, 10% scissors. A per-throw response chooses scissors (+0.30 rather than paper's +0.20). With one throw left and a one-point lead, paper yields expected match points 0.95, while scissors yields 0.85. The optimal objective really matters.

## End with a claim that fits the evidence

Ask each participant for one assumption, one measured result on fresh seeds and one limitation. Neither a leaderboard rank nor one lucky match establishes a universal strategy. Perfect independent uniform play remains the unexploitable theoretical baseline; the workshop's learning opportunities come from the personalities and dependencies of actual opponents.

The source repository contains facilitator reference bots and tests for the lesson mechanics. They are comparison tools, not required starting code or guaranteed tournament winners. Let participants explain and modify them if you choose to share them.
