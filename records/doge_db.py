#!/usr/bin/env python3
"""DOGE records CLI. DB: $DOGE_DB or ./wins.db next to this script; backup: $DOGE_BACKUP or ./backup next to the DB."""
import argparse,sqlite3,csv,os,sys,shutil,subprocess,datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__))
DB=os.environ.get('DOGE_DB',os.path.join(HERE,'wins.db'))
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
SCHEMA=os.path.join(HERE,'schema.sql')
def init(a):
    c=con(); have={r[0] for r in c.execute("select name from sqlite_master where type='table'")}
    for stmt in open(SCHEMA).read().split(';'):
        st=stmt.strip()
        if st and st.split()[2] not in have: c.execute(st)
    c.execute("insert or ignore into meta values('schema_version','9')"); c.commit(); c.close(); print('ready',DB)
def restore(a):
    c=con(); n=0
    for t in [r[0] for r in c.execute("select name from sqlite_master where type='table'")]:
        f=os.path.join(a.dir,t+'.csv')
        if not os.path.exists(f): continue
        rows=list(csv.reader(open(f,newline='')))
        if len(rows)<2: continue
        ph=','.join('?'*len(rows[0]))
        for r in rows[1:]: c.execute(f'insert or ignore into {t}({",".join(rows[0])}) values({ph})',[x if x!='' else None for x in r]); n+=1
    c.commit(); c.close(); print('restored rows (existing kept):',n)
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
a=p.parse_args(); a.f(a)
