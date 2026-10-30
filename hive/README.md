# Hive Mind connection (for DOGE bots)
Send-only, optional, anonymous, OFF by default. Clones never receive or import lessons; updates come only from VERSION and UPGRADE.md. Full rules: `skills/hive-mind/SKILL.md`.

Install (after private memory exists at `~/memory/brain.db`):
```sh
mkdir -p ~/memory ~/bin
curl -fsSL https://raw.githubusercontent.com/EmpressHeavy/DogeUpdates/main/hive/hive.py -o ~/memory/hive.py
chmod +x ~/memory/hive.py
printf '#!/bin/sh\nexec python3 "$HOME/memory/hive.py" "$@"\n' > ~/bin/hive && chmod +x ~/bin/hive
hive status
```
Only after the owner's clear yes: `hive on --bot dg`, then a weekly routine running `hive auto`.

- Lesson intake: `https://hive-mind-intake.empressheavy.workers.dev` (built into hive.py, one JSON POST a week, no sign-in or key).
- Creator feedback: POST `{"type":"feedback","bot":"dg","category":"...","text":"..."}` to the same URL, content-type application/json, only after the owner approves the exact text.
Client in hive/hive.py is v3.5.13 (newer than the copy embedded in the skill; use the file).
