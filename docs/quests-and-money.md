# Wins, quests, bonus points, money recovered (v9 logic)
- Day record: date (owner's time zone), day of week, wins (5 asked, any number accepted), quests, quests done, bonus points, daily total, notes.
- Each completed quest = 1 bonus point. Daily total = wins + bonus points (`doge_db.py` recalculates on every write).
- Quests can be added anytime (`add-quest`); asked about at each evening check-in; completed with `complete-quest`; unfinished ones are offered to carry to tomorrow (never a penalty).
- Late logging: allowed for yesterday (`--date`); ask which day when unclear. Never overwrite a past day; ask before replacing.
- Digital quests DOGE does itself (payout/royalty balances, payout emails, forgotten platforms, simple forms, unclaimed-property research) count as completed quests.
- Money recovered: platform, amount, date, status, notes (`add-money`). Statuses starting "Received" count toward the received total; "Saved monthly" toward monthly savings (`totals`). Celebrate every dollar.
- Unclaimed balances already turned over to the state: point the owner to their state's official unclaimed property site or missingmoney.com.
- Every write goes to wins.db immediately and is backed up immediately; never batch nightly.
