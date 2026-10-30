---
name: private-memory-db
description: >-
  Use at the start of every task and whenever you learn something durable: sets
  up and uses this bot's own private SQLite memory (brain.db plus a mem CLI)
  with an optional GitHub backup.
---
# Private memory database
Each owner gets their own empty, private memory on their bot's computer. Never copy another owner's data into it.

## Setup (first run, if `~/memory/brain.db` is missing)
1. `mkdir -p ~/memory ~/bin`. Write the CLI below to `~/memory/mem`, `chmod +x` it, and symlink it to `~/bin/mem`.
2. Run `mem init`, then `mem log setup "memory created"`.

```python
#!/usr/bin/env python3
import sqlite3,sys,os,datetime
DB=os.path.expanduser('~/memory/brain.db')
c=sqlite3.connect(DB);c.execute('PRAGMA journal_mode=WAL')
now=datetime.datetime.now().isoformat(timespec='seconds')
a=sys.argv[1:] or ['help'];cmd=a[0]
if cmd=='init':
  c.executescript('''CREATE TABLE IF NOT EXISTS fact(id INTEGER PRIMARY KEY,subject TEXT,predicate TEXT,value TEXT,valid_from TEXT,valid_to TEXT);
CREATE TABLE IF NOT EXISTS rule(id INTEGER PRIMARY KEY,category TEXT,text TEXT,set_on TEXT,active INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS project(id INTEGER PRIMARY KEY,title TEXT,status TEXT,path TEXT,notes TEXT,updated TEXT);
CREATE TABLE IF NOT EXISTS log(id INTEGER PRIMARY KEY,ts TEXT,kind TEXT,text TEXT);''')
elif cmd=='fact':
  s,p,v=a[1:4]
  with c:
    c.execute('UPDATE fact SET valid_to=? WHERE subject=? AND predicate=? AND valid_to IS NULL',(now,s,p))
    c.execute('INSERT INTO fact(subject,predicate,value,valid_from) VALUES(?,?,?,?)',(s,p,v,now))
elif cmd=='rule':
  with c: c.execute('INSERT INTO rule(category,text,set_on) VALUES(?,?,?)',(a[1],a[2],now))
elif cmd=='project':
  with c: c.execute('INSERT INTO project(title,status,path,notes,updated) VALUES(?,?,?,?,?)',(a[1],a[2],a[3] if len(a)>3 else '',a[4] if len(a)>4 else '',now))
elif cmd=='log':
  with c: c.execute('INSERT INTO log(ts,kind,text) VALUES(?,?,?)',(now,a[1],a[2]))
elif cmd=='q':
  for r in c.execute(a[1]): print('|'.join(map(str,r)))
elif cmd=='boot':
  for t,q in [('RULES','SELECT category,text FROM rule WHERE active=1'),('FACTS','SELECT subject,predicate,value FROM fact WHERE valid_to IS NULL'),('PROJECTS',"SELECT id,title,status,path FROM project WHERE status!='done'"),('RECENT','SELECT ts,kind,text FROM log ORDER BY id DESC LIMIT 10')]:
    print('##',t)
    for r in c.execute(q): print('|'.join(map(str,r)))
else: print('mem init|boot|fact S P V|rule CAT TEXT|project TITLE STATUS [PATH] [NOTES]|log KIND TEXT|q SQL')
```

## Every task
- Start with `mem boot`, then `mem q` for anything specific.
- Write facts as they happen, not in batches: `mem fact`, `mem rule`, `mem project`, `mem log`. `mem fact` closes the old current value automatically, so rows are never deleted.
- To change a project's status, run a short `UPDATE project SET status=?,updated=? WHERE id=?` in python3 sqlite3, then `mem log`.
- Never store passwords, PINs, tokens, SSNs, or full card numbers. Write "in vault" or the last 4 digits only.

## Optional GitHub backup
Only if the owner asks for it and connects GitHub: create a **private** repo they own. Export with `python3 -c` (`iterdump()` to `~/memory/export/dump.sql`), commit only the export folder, and push. Ask before the first push, and confirm the repo is private.
