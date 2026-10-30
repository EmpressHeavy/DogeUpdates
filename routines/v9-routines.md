# DOGE v9 routines (created at the end of setup, owner's time zone)
| # | Routine | When | What | Created if |
|---|---|---|---|---|
| 1 | Daily check-in | 20:40 daily (default; owner's chosen time) | Ask "What are 5 things you got done today?", ask about each open quest, log with doge_db.py, offer to carry unfinished quests to tomorrow, add a Journal task-log line | Always |
| 2 | Monthly settings check | 1st, 10:00 | Connectors, backup health, extra emails, Hive Mind on/off, feedback offer, update check | Always |
| 3 | Sunday digest | Sun 18:00 (owner's choice) | Week's wins, bonus points, money (`week`, `totals`); spending pie via `spending_pie.py` if "where your money goes" is on | Owner wants it |
| 4 | Daily money watch | 11:30 daily | Scan connected inboxes for real payouts/balances (verify sender + domain, open official site directly) | Money hunts on |
| 5 | X Chat watch | every 2h 08:00–20:00 | Report important DMs per xchat-watch-and-send | Owner wants it |
| 6 | Weekly file backup | Weekly | Send fresh wins.db + CSV zip (+ journal) | Owner chose "Send me the file weekly" |
| 7 | Hive Mind weekly share | Weekly | `hive auto`, silent unless it fails | Hive Mind clearly turned on |
| 8 | DOGE weekly update check | Weekly | See weekly-update-check.md | Always after v9 upgrade |

Exact prompts: routines/v9-routine-prompts.md (same numbering). The creator's Friday feedback digest is owner-only and not shipped.
