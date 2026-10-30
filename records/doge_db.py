#!/usr/bin/env python3
"""DOGE records CLI (generic, data-free). DB: $DOGE_DB or /workspace/records/wins.db; backup dir: $DOGE_BACKUP or ./backup next to the DB.
First run: python3 doge_db.py init. Restore from a backup folder of CSVs (additive, never overwrites): python3 doge_db.py restore <dir>.
Spending: add-spend / import-spend <csv> / spend-summary <start>; chart with spending_pie.py."""
import argparse,sqlite3,csv,os,sys,shutil,subprocess,datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__))
DB=os.environ.get('DOGE_DB','/workspace/records/wins.db')
BK=os.environ.get('DOGE_BACKUP',os.path.join(os.path.dirname(os.path.abspath(DB)),'backup'))
con=lambda: sqlite3.connect(DB)
dow=lambda d: dt.date.fromisoformat(d).strftime('%A')
today=lambda: dt.date.today().isoformat()
def ensure_day(c,d): c.execute('insert or ignore into days(date,day_of_week,bonus_points,daily_total) values(?,?,0,0)',(d,dow(d)))
def recalc(c,d):
    w=c.execute('select count(*) from wins where date=?',(d,)).fetchone()[0]
    b=c.execute('select count(*) from quests where date=? and done=1',(d,)).fetchone()[0]
    c.execute('update days set bonus_points=?,daily_total=? where date=?',(b,w+b,d))
def export_csv(out):
    os.makedirs(out,exist_ok=True); c=con()
    for (t,) in c.execute("select name from sqlite_master where type='table'").fetchall():
        cur=c.execute(f'select * from {t}')
        with open(os.path.join(out,f'{t}.csv'),'w',newline='') as f:
            w=csv.writer(f); w.writerow([x[0] for x in cur.description]); w.writerows(cur)
    c.close(); return out
def backup(msg):
    export_csv(BK); shutil.copy2(DB,os.path.join(BK,'wins.db'))
    if not os.path.isdir(os.path.join(BK,'.git')): return
    g=lambda *a: subprocess.run(['git','-C',BK,*a],capture_output=True,text=True)
    if not g('remote').stdout.strip(): return
    g('add','-A')
    if g('diff','--cached','--quiet').returncode==0: return
    g('commit','-m',msg)
    for i in range(3):
        r=g('push','origin','HEAD')
        if r.returncode==0: print('backup pushed'); return
    print('WARNING: backup push failed (tell the user): '+r.stderr.strip(),file=sys.stderr)
def write(fn):
    def w(a):
        c=con(); msg=fn(c,a); c.commit(); c.close(); print(msg); backup(msg)
    return w
@write
def add_win(c,a):
    d=a.date or today(); ensure_day(c,d)
    i=c.execute('select coalesce(max(idx),0)+1 from wins where date=?',(d,)).fetchone()[0]
    c.execute('insert into wins values(?,?,?)',(d,i,a.text)); recalc(c,d); return f'win {d} #{i}: {a.text}'
@write
def add_quest(c,a):
    d=a.date or today(); ensure_day(c,d); c.execute('insert into quests(date,text,done) values(?,?,0)',(d,a.text)); return f'quest {d}: {a.text}'
@write
def complete_quest(c,a):
    d=a.date or today()
    rows=c.execute('select rowid,text from quests where date=? and done=0 and text like ?',(d,f'%{a.match}%')).fetchall()
    if len(rows)!=1: sys.exit(f'{len(rows)} open quests on {d} match {a.match!r}: '+'; '.join(r[1] for r in rows))
    c.execute("update quests set done=1,status='Done (+1 bonus)' where rowid=?",(rows[0][0],)); recalc(c,d)
    return f'quest done {d}: {rows[0][1]}'
@write
def add_money(c,a):
    c.execute('insert into money values(?,?,?,?,?)',(a.platform,a.amount,a.date or today(),a.status,a.notes)); return f'money: {a.platform} {a.amount}'
def day(a):
    c=con(); r=c.execute('select * from days where date=?',(a.date,)).fetchone()
    if not r: print('no record'); return
    print(f'{r[0]} {r[1]}  total={r[4]} bonus={r[3]}')
    for i,t in c.execute('select idx,text from wins where date=? order by idx',(a.date,)): print(f'  win {i}: {t}')
    for t,dn,ct in c.execute('select text,done,carried_to from quests where date=?',(a.date,)): print(f"  quest [{'x' if dn else ' '}] {t}"+(f' -> {ct}' if ct else ''))
def week(a):
    s=dt.date.fromisoformat(a.start); e=(s+dt.timedelta(days=6)).isoformat(); c=con()
    rows=c.execute('select date,day_of_week,(select count(*) from wins w where w.date=d.date),bonus_points,daily_total from days d where date between ? and ? order by date',(a.start,e)).fetchall()
    for r in rows: print(f'{r[0]} {r[1]:9} wins={r[2]} bonus={r[3]} total={r[4]}')
    print('week total:',sum(r[4] or 0 for r in rows))
def totals(a):
    c=con(); q=lambda s: c.execute(s).fetchone()[0]
    print('days',q('select count(*) from days'),'| wins',q('select count(*) from wins'),'| quests done',q('select sum(done) from quests'),'/',q('select count(*) from quests'))
    print('money received/payouts total: $%.2f'%q("select coalesce(sum(amount),0) from money where status like 'Received%'"))
    print('monthly savings: $%.2f/mo'%q("select coalesce(sum(amount),0) from money where status like 'Saved monthly%'"))
SCHEMA="""create table days(date text primary key, day_of_week text, quests_done text, bonus_points real, daily_total real, notes text);
create table wins(date text, idx integer, text text, primary key(date,idx));
create table quests(date text, text text, done integer default 0, carried_to text, status text);
create table money(platform text, amount real, date text, status text, notes text);
create table goals(goal text, type text, target real, progress real, start_date text, target_date text, notes text, percent_done text);
create table log_archive(date text, type text, item text, notes text);
create table spending_categories(category text, amount real, pct_of_total text);
create table spending_transactions(date text, merchant text, category text, amount real, account text);
create table meta(key text primary key, value text);"""
def init(a):
    os.makedirs(os.path.dirname(os.path.abspath(DB)),exist_ok=True); c=con()
    for st in SCHEMA.split(';'):
        st=st.strip()
        if st: c.execute(st.replace('create table ','create table if not exists ',1))
    c.execute("insert or ignore into meta values('schema_version','9')"); c.commit(); c.close(); print('db ready:',DB)
def restore(a):
    """Additive: adds rows from <dir>/<table>.csv that aren't already there. Never deletes or overwrites existing rows."""
    init(a); c=con(); n={}
    for (t,) in c.execute("select name from sqlite_master where type='table'").fetchall():
        f=os.path.join(a.dir,f'{t}.csv')
        if not os.path.exists(f): continue
        with open(f,newline='') as fh:
            r=csv.reader(fh); h=next(r,None); rows=[[v if v!='' else None for v in x] for x in r]
        if not h: continue
        have={tuple(None if v is None else str(v) for v in y) for y in c.execute(f'select {",".join(h)} from {t}')}
        norm=lambda x: tuple(None if v is None else (str(float(v)) if v.replace('.','',1).lstrip('-').isdigit() and '.' in v else v) for v in x)
        add=[x for x in rows if norm(x) not in have and tuple(x) not in have]
        c.executemany(f'insert or ignore into {t}({",".join(h)}) values({",".join("?"*len(h))})',add); n[t]=len(add)
    c.commit(); c.close(); print('restored (added, existing kept):',n)
def _spend_row(c,d,merchant,cat,amt,acct):
    if c.execute('select 1 from spending_transactions where date=? and merchant=? and amount=? and coalesce(account,"")=coalesce(?,"")',(d,merchant,amt,acct)).fetchone(): return 0
    c.execute('insert into spending_transactions values(?,?,?,?,?)',(d,merchant,cat,amt,acct)); return 1
@write
def add_spend(c,a):
    n=_spend_row(c,a.date or today(),a.merchant,a.category,abs(a.amount),a.account)
    return f'spend {a.merchant} {abs(a.amount):.2f} [{a.category}]'+('' if n else ' (already logged, skipped)')
@write
def import_spend(c,a):
    """CSV with header date,merchant,category,amount[,account]. Purchases only; duplicates skipped."""
    n=k=0
    with open(a.file,newline='') as fh:
        for r in csv.DictReader(fh):
            k+=1; n+=_spend_row(c,r['date'],r['merchant'],r.get('category') or 'Other',abs(float(r['amount'])),r.get('account') or a.account)
    return f'spending import: {n} added, {k-n} duplicates skipped'
@write
def spend_summary(c,a):
    """Adds a dated category snapshot to spending_categories (rows are labelled with the window; older snapshots stay)."""
    s,e=a.start,a.end or today()
    rows=c.execute('select category,sum(amount) from spending_transactions where date between ? and ? group by category order by 2 desc',(s,e)).fetchall()
    tot=sum(r[1] for r in rows) or 1
    for cat,amt in rows: c.execute('insert into spending_categories values(?,?,?)',(f'{cat} ({s}..{e})',round(amt,2),f'{amt*100/tot:.1f}%'))
    return 'spending '+s+'..'+e+': '+'; '.join(f'{k} ${v:.2f}' for k,v in rows)
p=argparse.ArgumentParser(); s=p.add_subparsers(dest='cmd',required=True)
x=s.add_parser('add-win'); x.add_argument('text'); x.add_argument('--date'); x.set_defaults(f=add_win)
x=s.add_parser('add-quest'); x.add_argument('text'); x.add_argument('--date'); x.set_defaults(f=add_quest)
x=s.add_parser('complete-quest'); x.add_argument('match'); x.add_argument('--date'); x.set_defaults(f=complete_quest)
x=s.add_parser('add-money'); x.add_argument('platform'); x.add_argument('amount',type=float); x.add_argument('--date'); x.add_argument('--status',default=''); x.add_argument('--notes'); x.set_defaults(f=add_money)
x=s.add_parser('day'); x.add_argument('date'); x.set_defaults(f=day)
x=s.add_parser('week'); x.add_argument('start'); x.set_defaults(f=week)
s.add_parser('totals').set_defaults(f=totals)
x=s.add_parser('export-csv'); x.add_argument('dir'); x.set_defaults(f=lambda a: print('exported to',export_csv(a.dir)))
s.add_parser('init').set_defaults(f=init)
x=s.add_parser('restore'); x.add_argument('dir'); x.set_defaults(f=restore)
x=s.add_parser('add-spend'); x.add_argument('merchant'); x.add_argument('amount',type=float); x.add_argument('--category',default='Other'); x.add_argument('--date'); x.add_argument('--account'); x.set_defaults(f=add_spend)
x=s.add_parser('import-spend'); x.add_argument('file'); x.add_argument('--account'); x.set_defaults(f=import_spend)
x=s.add_parser('spend-summary'); x.add_argument('start'); x.add_argument('--end'); x.set_defaults(f=spend_summary)
x=s.add_parser('backup'); x.set_defaults(f=lambda a: backup('manual backup'))
a=p.parse_args(); a.f(a)
