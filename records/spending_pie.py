#!/usr/bin/env python3
"""DOGE spending pie chart. Reads spending_transactions (purchases) from wins.db for a date window and writes a PNG.
Usage: python3 spending_pie.py [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--out spending.png]
Default window: last 30 days. Falls back to the latest spending_categories rows if there are no transactions.
Needs matplotlib (python3 -m pip install --user matplotlib). Read-only: never writes to the database."""
import argparse, os, sqlite3, datetime as dt
p = argparse.ArgumentParser()
p.add_argument('--db', default=os.environ.get('DOGE_DB', '/workspace/records/wins.db'))
p.add_argument('--start'); p.add_argument('--end'); p.add_argument('--out', default='/workspace/records/spending.png')
p.add_argument('--top', type=int, default=7, help='categories shown before the rest are grouped as Other')
a = p.parse_args()
end = a.end or dt.date.today().isoformat()
start = a.start or (dt.date.fromisoformat(end) - dt.timedelta(days=30)).isoformat()
c = sqlite3.connect(f'file:{a.db}?mode=ro', uri=True)
rows = c.execute("select coalesce(nullif(category,''),'Other'), sum(amount) from spending_transactions "
                 "where date between ? and ? group by 1 having sum(amount)>0 order by 2 desc", (start, end)).fetchall()
label = f'{start} to {end}'
if not rows:
    rows = c.execute("select category, amount from spending_categories where amount>0 order by rowid desc limit 20").fetchall()
    label = 'latest saved categories'
if not rows:
    raise SystemExit('no spending data yet')
if len(rows) > a.top:
    rows = rows[:a.top] + [('Other', sum(r[1] for r in rows[a.top:]))]
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
total = sum(r[1] for r in rows)
fig, ax = plt.subplots(figsize=(7, 7))
ax.pie([r[1] for r in rows], labels=[f'{r[0]}\n${r[1]:,.0f}' for r in rows], autopct='%1.0f%%', startangle=90, counterclock=False)
ax.set_title(f'Where your money went ({label})\nTotal ${total:,.2f}')
fig.savefig(a.out, dpi=120, bbox_inches='tight')
print(f'wrote {a.out}; top category: {rows[0][0]} ${rows[0][1]:,.2f} of ${total:,.2f}')
