# DOGE v9 routines (created at the end of setup, owner's time zone)
| # | Routine | When | What | Created if |
|---|---|---|---|---|
| 1 | Daily check-in | 20:40 daily (default; owner's chosen time) | Ask "What are 5 things you got done today?", ask about each open quest, log with doge_db.py, offer to carry unfinished quests to tomorrow, add a Journal task-log line | Always |
| 2 | Monthly settings check | 1st, 10:00 | Connectors, backup health, extra emails, all settings + Hive Mind status, multi-select card to flip settings, feedback offer, re-create update-check routine if missing | Always |
| 3 | Sunday digest | Sun 18:00 (owner's choice) | Week's wins, bonus points, money (`week`, `totals`); spending pie via `spending_pie.py` if "where your money goes" is on | Owner wants it |
| 4 | Daily money watch | 11:30 daily | Scan connected inboxes for real payouts/balances (verify sender + domain, open official site directly) | Money hunts on |
| 5 | X Chat watch | every 2h 08:00–20:00 | Report important DMs per xchat-watch-and-send | Owner wants it |
| 6 | Weekly file backup | Weekly | Send fresh wins.db + CSV zip (+ journal) | Owner chose "Send me the file weekly" |
| 7 | Hive Mind weekly share | Weekly | `hive auto`, silent unless it fails | Default on at setup; only while Hive Mind is on (deleted if turned off) |
| 8 | DOGE weekly update check | Sun 10:00 | Auto-apply newer VERSION from this repo (snapshot, rollback), then a "DOGE updated to vN" note | Always (mandatory, can't be turned off; monthly check re-creates it) |

Exact prompts: routines/v9-routine-prompts.md (same numbering). The creator's Friday feedback digest is owner-only and not shipped.
