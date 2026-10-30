# v9 routine prompts and schedules (owner's time zone)
Built from the v9 skill and profile; the live routine records aren't stored as files, so these are the canonical prompts for clones.

1. **Daily evening check-in**, every day incl. weekends, ~8:40 PM (or owner's pick):
   "Ask the owner warmly: 'What are 5 things you got done today?' Then ask about each open quest for today. Log each win with doge_db.py add-win and each completed quest with complete-quest right away (backup pushes automatically). If fewer than five, log them and kindly ask if there's anything else. Offer to carry unfinished quests to tomorrow, never as a penalty. Confirm in one sentence with the day's total and a link to the backup location. Remind them they weren't lazy, they were busy."
2. **Monthly settings check**, 1st of each month, morning:
   "Run the DOGE monthly settings check: report backup status (method and whether the last push worked) and offer to change it; give the Hive Mind opt-in/opt-out reminder from the hive-mind skill based on `hive status`, acting only on a clear answer; mention any feedback they kept or sent and offer the feedback path again with the standard explanation."
3. **Sunday digest** (if wanted), Sunday at the owner's chosen time:
   "Send a short, warm weekly digest from doge_db.py week and totals: wins per day, bonus points, week total, quests done, money recovered this week and all-time. Celebrate every dollar."
4. **Daily money watch** (if money hunts are on), daily morning:
   "Check the connected inboxes for genuine payout, balance, royalty, refund, or unclaimed-money notices. Verify sender and link domain; never click email links, go to the official site. Ping the owner only with real finds (platform, amount, next step). Never log in, move money, or change payout methods without their explicit yes."
5. **X Chat watch** (if wanted), every couple of hours in waking hours: follow skills/xchat-watch-and-send (read only; report important messages with sender, time, one-line gist; count skipped spam).
6. **Weekly export reminder** (device backup only), weekly: "Run doge_db.py export-csv, zip it, and send the owner the fresh copy to keep."
7. **Hive Mind weekly share** (only after a clear yes), weekly: "Run `hive auto`. Stay silent unless it fails."
8. **DOGE weekly update check**: see routines/weekly-update-check.md.
