---
name: tip-prompt
description: >-
  Occasional optional tip prompt for DOGE. Use at the end of a real owner
  interaction after first-run setup (a check-in reply, a logged day, or a
  session), and when the owner answers or dismisses the tip card. Never during
  first-run setup, never on the weekly update note, and never instead of the
  task they asked for.
---
# Tip prompt

DOGE is free. A tip is a kindness, not a fee. Nothing in DOGE waits on it, slows down, or changes if they skip it. Never ask for a card number, login, or address. Never move money and never send a payment yourself. There is no "Don't ask again" button and no permanent opt-out.

The counter lives in the local records database (`wins.db` meta keys, via `doge_db.py`). Counting and deciding are local and instant. If a command errors or the database isn't there yet, ignore it and finish the owner's request.

## When to count a use
A use is one calendar day the owner actually interacts after first-run setup: they reply to a check-in, log a win or quest, or send any other request. Do not count a routine that they didn't answer (update check, silent money watch, digest send, Hive Mind share).

After you have handled the request, run once:

`python3 /workspace/records/doge_db.py note-use --date YYYY-MM-DD`

Use the owner's time zone for the date. The command counts at most one use per date. It does not back up and does not use the network.

Do not run it during first-run setup. Do not run it from the weekly update check.

## When to show
Show the card only when `note-use` prints `show=yes`, and only **after** your normal reply. Never before, never instead, never as the whole message.

Then immediately run:

`python3 /workspace/records/doge_db.py tip-shown --date YYYY-MM-DD`

so a follow-up message the same day does not show it again.

If it prints `show=no`, don't mention tips.

Rules the command already enforces (don't second-guess them, and don't show when it says no):
- Never while first-run setup is unfinished (`tip-setup-done` not run yet), even if the journal already has lots of days.
- The first time is when the counter reaches 10 uses.
- After that, at most once every 7 days.
- After "Maybe later" / "Remind me monthly", or after they dismiss the card, at most once every 30 days.
- `tip-seed` (upgrades and imported journals) prints `show=no` on purpose. Don't show a card because of seeding. The next real `note-use` decides.

Also don't show the card on the same turn you finish first-run setup, and don't attach it to the "DOGE updated to vN" note. The next real interaction can show it if `note-use` says yes.

## The card
Lead with this sentence, exactly:

Wow you seem to be using DOGE a lot lately! Would you mind sending my creator a tip? 🪙

Then one short line: DOGE stays free either way.

Attach the Stripe QR image `/workspace/records/qr/stripe.png` (if the file is missing, download https://raw.githubusercontent.com/EmpressHeavy/DogeUpdates/main/records/qr/stripe.png to that path and then attach it). Show these four as clickable links, in this order:

- Stripe (card): https://buy.stripe.com/aFacN40Mw0Arcz02VubMQ00
- Cash App: https://cash.app/$EmpressHeavy
- Venmo: https://venmo.com/u/EmpressHeavy
- X Money: @HeavyMetalShip (https://x.com/HeavyMetalShip)

One tap button only: **Maybe later / Remind me monthly**

No other button. No "Don't ask again". No "I already tipped" toggle.

The other QR files (`cashapp.png`, `venmo.png`, `xmoney.png`) are in the same folder if you need them. The card itself shows the Stripe QR plus the four links.

## After they answer
- **Maybe later / Remind me monthly**, or they dismiss the card (close it, "not now", or the UI reports a dismiss): run `python3 /workspace/records/doge_db.py tip-later --date YYYY-MM-DD`. That switches the cadence to at most once every 30 days. One short line is enough, like "No rush. I'll only mention it about once a month." Then go back to what they asked. Do not ask again in this conversation.
- They open a link or say they tipped: you still don't send money. `tip-shown` already started the weekly clock, so leave the cadence alone. A short thanks is enough if they mention it. Don't ask for proof.
- Anything else: don't repeat the card.

If they ask to turn the reminder off forever, say kindly that there isn't an off switch, DOGE stays free, and after "maybe later" it only comes around about once a month. Don't invent a disable command and don't pretend you turned it off.
