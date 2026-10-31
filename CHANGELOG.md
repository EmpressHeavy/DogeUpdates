# Changelog

## 11
- Hive Mind is now ON by default for new setups: DOGE installs the client, turns it on (`hive on --bot dg`), confirms status, and creates the silent "Hive Mind weekly share" routine, then sends a short plain notice. No opt-in card or question.
- If you ask to turn it off, DOGE shows a "Why leave this on?" card (Keep Hive Mind on / Turn off Hive Mind); turning off runs `hive off` and deletes the weekly routine. You can turn it back on anytime.
- Monthly settings check now shows all your settings plus Hive Mind status, then one multi-select card to flip any on/off setting; nothing changes unless you pick it.
- Existing owners: updates keep your current Hive Mind choice; nothing else changes. Still send-only and anonymous.

## 10
- Updates are now automatic and always on: every DOGE has a weekly update-check routine that installs newer versions from this repo by itself and sends you a short "DOGE updated to vN, here's what's new" note. It can't be turned off (you can move its time); the monthly settings check re-creates it if it's missing.
- Every update takes a snapshot first and rolls back if anything fails. Your records, past days, and the optional settings you chose stay as they are; new optional settings start off and are offered as a card.
- Includes the Oct 30 v9 rebuild: new profile and welcome message, simpler setup (GitHub or weekly-file backup), spending tracking with a pie chart, a DOGE Journal (Backup Brain) template, and install steps.

## 9 (rebuilt Oct 30, 2026 from the final v9 build)
- Profile: new name, title "Daily wins, quests & small-money finder", welcome message (`profile/welcome_message.txt`), generic description that starts with "run setup first".
- Setup skill: runs on any first message; avatar step first; no Google step; backup is GitHub (default) or a weekly file; journal, spending, and install steps added.
- `doge_db.py`: `restore` is additive (never deletes or overwrites rows); new `add-spend`, `import-spend`, `spend-summary`; `init` records schema_version 9.
- New `records/spending_pie.py` (matplotlib pie chart of spending, read-only).
- New blank DOGE Journal (Backup Brain) template, append-only.
- Hive Mind is send-only (clones never receive lessons) with a behavior-based report trigger.
- Weekly update check against this repo.

### Build notes (internal, Oct 26 to 29)
- Records move from Google Sheets to local SQLite (/workspace/records/wins.db) via bundled doge_db.py (new `init`, `restore`, `backup` commands; data-free, no personal paths).
- Required backup at setup (no skip): GitHub private repo (recommended), CSV folder in user's cloud drive, or device download with weekly reminder.
- Write-through: every win/quest/money entry is saved and backed up immediately; restore after any wipe.
- New "Have you used DOGE before?" upgrade path (restore from backup or old bot export via SendToAgent).
- Existing Sheets users migrated to SQLite; Sheet is never written to again and never deleted.
- Sheet styling question and sheet link removed; final confirmation links to the backup location.
- Hive Mind offer gains Bot Terminator v3.5.0 "Why leave this on?" wording (hive id `dg`); new opt-in "Send feedback to the creator" draft-card flow.
- Kept: avatar step, X Chat watch, money hunts, safety rules, monthly settings check (now also backup status + feedback).
- Feedback now goes through the Hive Mind server (`hive feedback`), not email; the creator reviews it.

#### Oct 29, 2026 fixes (new-owner install issues)
- Real PNG avatar (`profile/avatar.png`); the setup avatar step is a fallback that tells the owner if it fails.
- Welcome message + generic new-owner description/profile (no personal details, no Sheets setup; local SQLite records); description starts with the run-setup-first line.
- Restored skill frontmatter; description now says to run on any first message.
- Hive Mind: DOGE uses its own code dg (separate DB if another bot's client is on the computer); feedback prefers `hive feedback add`, falls back to the JSON POST.

#### Oct 29, 2026 (after a test install)
- Removed the Google account step from core setup; Google only comes up later for a Google-based digital quest or a legacy Sheet migration.
- Backup step: default is the SQLite file on DOGE's computer + automatic backup to the owner's private GitHub repo; cloud-drive/spreadsheet option removed; one-line weekly-file fallback for owners without GitHub. Setup steps renumbered (backup is now step 4).

#### Oct 29, 2026 (GitHub backup, no user repo work)
- Backup step is a widget card (GitHub recommended / weekly file). GitHub path: `cursor-github` `connect_github` card (sign in with Google, GitHub, or new account), then DOGE creates a private `my-doge-backup` (test: `my-doge-test-backup`) itself, does the first push, and confirms with a link. Owner never creates a repo or pastes a link; weekly file only if connect or repo setup fails.

#### Oct 29, 2026 (GitHub backup via gh device login)
- Replaced connect_github / connector repo creation with the gh CLI: install gh to ~/bin if missing, `gh auth login --web` device code sent in one message with the github.com/login/device link, `gh auth setup-git`, DOGE runs `gh repo create my-doge-backup --private` (test: my-doge-test-backup), verifies PRIVATE, first push, link in one line. One fresh code on expiry, then weekly file fallback. Token is never printed or stored.

#### Oct 29, 2026 (avatar never set on DOGE Test 2)
- Avatar is now Step 0: always run (no "if no picture shows" condition), done by DOGE itself before any question or delegation: curl the .jpg to /workspace/doge-avatar.jpg, UpdateAvatar action "set" with that local path, verify, one-line result.

## 2–8
Internal builds; changes are included in 9.

## 1
Original template: evening "5 things" check-in, quests and bonus points, money-recovered tab, all in a Google Sheet.
