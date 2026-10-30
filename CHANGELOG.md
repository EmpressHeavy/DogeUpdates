# Changelog

## 9
- Records move from Google Sheets to a private SQLite store (`records/doge_db.py`, `wins.db`): days, wins, quests, money, goals, spending, journal log, meta. New `init` and `restore` commands.
- Every write is backed up right away; required backup choice at setup (private GitHub repo, your cloud drive, or your device).
- Private memory (`brain.db` + `mem` CLI) via the private-memory-db skill.
- New first-run setup cards: name, previous-DOGE import, check-in time and time zone, connections, journal, goals, extra payout emails, money hunts, spending view, optional bank help, optional message sending, optional X Chat watch, Sunday digest, research OK, Hive Mind (off by default).
- Import from older DOGE bots, a Google Sheet, CSVs, or a GitHub backup without overwriting anything. Old Sheet kept untouched.
- Optional anonymous feedback to the creator.
- Weekly update check against this repo.

## 2–8
Internal builds; changes are included in 9.

## 1
Original template: evening "5 things" check-in, quests and bonus points, money-recovered tab, all in a Google Sheet.
