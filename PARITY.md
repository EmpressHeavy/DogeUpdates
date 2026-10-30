# v9 parity map
| v9 component | Repo location |
|---|---|
| Agent profile (name, title, description, avatar shape/color) | `profile/profile.json` (owner details are placeholders) |
| Per-agent settings | `profile/settings.json` |
| Profile picture | `profile/avatar.png` (also `skills/doge-getting-started/doge-avatar.jpg`, used by first-run) |
| First-run setup flow and all setup cards | `skills/doge-getting-started/SKILL.md`; verbatim card text in `docs/setup-cards.md` |
| "Have you used DOGE before?" card | setup card 2 (`docs/setup-cards.md`, `docs/voice-and-phrases.md`) |
| Tone and signature phrases | `docs/voice-and-phrases.md` |
| Wins, quests, bonus points, money-recovered logic | `docs/quests-and-money.md`, `records/doge_db.py` |
| Records store (SQLite) and schema | `records/doge_db.py`, `records/schema.sql` |
| Private memory (brain.db + mem) | `skills/private-memory-db/SKILL.md` |
| Backup (GitHub / cloud / device) | setup card 5; `doge_db.py` auto-push |
| Moving from Google Sheets / older DOGE | `skills/doge-getting-started/SKILL.md` ("Moving from Google Sheets"), `UPGRADE.md` step 3 |
| Hive Mind (send-only client, opt-in, report trigger) | `skills/hive-mind/SKILL.md`, `hive/hive.py`, `hive/README.md` |
| Creator feedback | `skills/doge-getting-started/SKILL.md`, `hive/README.md` |
| X Chat watch and send | `skills/xchat-watch-and-send/SKILL.md` |
| Routines and exact prompts | `routines/v9-routines.md`, `routines/v9-routine-prompts.md` |
| Weekly update check | `routines/weekly-update-check.md` |
| Monthly settings check | `skills/doge-getting-started/SKILL.md`, `routines/v9-routine-prompts.md` |
| Safety rules | `docs/safety.md`, `UPGRADE.md` guardrails |
| Upgrade procedure | `UPGRADE.md` |
| Version | `VERSION`, `CHANGELOG.md` |

Built-in platform skills DOGE also relies on (provided by Grok Bot itself, not shipped here): x-api-mcp-guide, sign-in, vault, in-chat-forms, purchases, send-on-behalf, routines, no-connector-fallback.
