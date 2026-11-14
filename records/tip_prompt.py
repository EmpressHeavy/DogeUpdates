#!/usr/bin/env python3
"""Occasional DOGE tip prompt. Local counter in wins.db meta (same store as the journal).

A use is one calendar day the owner actually interacts after first-run setup.
The card shows the first time the counter reaches 10, then at most once every
7 days. "Maybe later" keeps that 7-day cadence (shows again next week).
"Remind me monthly", or dismissing the card without picking a button, switches
to at most once every 30 days. There is no "Don't ask again" and no permanent opt-out.

This never backs up, never touches the network, and never raises on a missing
database: callers get show=no and keep going. Tips are optional; DOGE stays free.

State keys in meta:
  tip_use_count, tip_setup_complete (1/0), tip_last_use_date,
  tip_last_shown (YYYY-MM-DD or empty), tip_cadence_days (7 or 30).
"""
import os, sqlite3, datetime as dt

FIRST_USES = 10
CADENCE_DAYS = 7
LATER_CADENCE_DAYS = 30

PROMPT = "Wow you seem to be using DOGE a lot lately! Would you mind sending my creator a tip? 🪙"
BUTTON_LATER = "Maybe later"
BUTTON_MONTHLY = "Remind me monthly"
BUTTONS = (BUTTON_LATER, BUTTON_MONTHLY)

# Public tip links only. The card shows the Stripe QR plus all four as links.
LINKS = (
    ("Stripe (card)", "https://buy.stripe.com/aFacN40Mw0Arcz02VubMQ00"),
    ("Cash App", "https://cash.app/$EmpressHeavy"),
    ("Venmo", "https://venmo.com/u/EmpressHeavy"),
    ("X Money", "https://x.com/HeavyMetalShip"),
)
X_MONEY_HANDLE = "@HeavyMetalShip"
QR_FILES = {
    "Stripe (card)": "stripe.png",
    "Cash App": "cashapp.png",
    "Venmo": "venmo.png",
    "X Money": "xmoney.png",
}
PRIMARY_QR = "stripe.png"

K_USES = "tip_use_count"
K_SETUP = "tip_setup_complete"
K_LAST_USE = "tip_last_use_date"
K_LAST_SHOWN = "tip_last_shown"
K_CADENCE = "tip_cadence_days"


def default_db():
    return os.environ.get("DOGE_DB", "/workspace/records/wins.db")


def qr_path(name=PRIMARY_QR):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "qr", name)


def _today(day):
    if day:
        dt.date.fromisoformat(day)  # validate
        return day
    return dt.date.today().isoformat()


def normalize_cadence(value):
    """Only 7 or 30. Anything else stays on the weekly cadence (no silent opt-out)."""
    try:
        n = int(value)
    except (TypeError, ValueError):
        return CADENCE_DAYS
    return LATER_CADENCE_DAYS if n == LATER_CADENCE_DAYS else CADENCE_DAYS


def evaluate(use_count, setup_complete, last_shown, cadence_days, today):
    """Pure cadence decision. today and last_shown are YYYY-MM-DD (last_shown may be empty)."""
    cadence = normalize_cadence(cadence_days)
    if not setup_complete:
        return False, "setup", cadence
    if int(use_count) < FIRST_USES:
        return False, "uses", cadence
    if not last_shown:
        return True, "first", cadence
    delta = (dt.date.fromisoformat(today) - dt.date.fromisoformat(last_shown)).days
    if delta >= cadence:
        return True, "due", cadence
    return False, "wait", cadence


def _line(uses, setup, show, cadence, reason):
    return f"uses={int(uses)} setup={1 if setup else 0} show={'yes' if show else 'no'} cadence={int(cadence)} reason={reason}"


def _connect(db_path):
    if not db_path or not os.path.exists(db_path):
        return None
    c = sqlite3.connect(db_path)
    c.execute("create table if not exists meta(key text primary key, value text)")
    return c


def _get(c, key, default=None):
    row = c.execute("select value from meta where key=?", (key,)).fetchone()
    return default if row is None else row[0]


def _put(c, key, value):
    c.execute(
        "insert into meta(key,value) values(?,?) on conflict(key) do update set value=excluded.value",
        (key, str(value)),
    )


def _days_stats(c):
    row = c.execute(
        "select 1 from sqlite_master where type='table' and name='days'"
    ).fetchone()
    if not row:
        return 0, ""
    n, last = c.execute("select count(*), coalesce(max(date),'') from days").fetchone()
    return int(n or 0), last or ""


def _read(c):
    uses = int(_get(c, K_USES, "0") or 0)
    setup = _get(c, K_SETUP, "0") == "1"
    last_use = _get(c, K_LAST_USE, "") or ""
    last_shown = _get(c, K_LAST_SHOWN, "") or ""
    cadence = normalize_cadence(_get(c, K_CADENCE, CADENCE_DAYS))
    return uses, setup, last_use, last_shown, cadence


def _ensure_defaults(c, seed_uses=None, seed_last_use=None, setup=None):
    """Fill only missing keys. Never overwrites a counter, a shown date, or a monthly cadence."""
    if _get(c, K_USES) is None:
        _put(c, K_USES, 0 if seed_uses is None else int(seed_uses))
    if _get(c, K_LAST_USE) is None:
        _put(c, K_LAST_USE, "" if seed_last_use is None else seed_last_use)
    if _get(c, K_LAST_SHOWN) is None:
        _put(c, K_LAST_SHOWN, "")
    if _get(c, K_CADENCE) is None:
        _put(c, K_CADENCE, CADENCE_DAYS)
    if setup is not None and _get(c, K_SETUP) is None:
        _put(c, K_SETUP, "1" if setup else "0")


def _closed(db_path, mutate):
    c = _connect(db_path)
    if c is None:
        return _line(0, False, False, CADENCE_DAYS, "no-db")
    try:
        out = mutate(c)
        c.commit()
        return out
    finally:
        c.close()


def note_use(db_path=None, day=None):
    """Count today once, after setup only. Returns the status line (show=yes/no)."""
    db_path = db_path or default_db()
    try:
        today = _today(day)
    except ValueError:
        return _line(0, False, False, CADENCE_DAYS, "bad-date")

    def mutate(c):
        _ensure_defaults(c)
        uses, setup, last_use, last_shown, cadence = _read(c)
        if not setup:
            show, reason, cadence = evaluate(uses, False, last_shown, cadence, today)
            return _line(uses, False, show, cadence, reason)
        if last_use != today:
            uses += 1
            last_use = today
            _put(c, K_USES, uses)
            _put(c, K_LAST_USE, last_use)
        show, reason, cadence = evaluate(uses, True, last_shown, cadence, today)
        return _line(uses, True, show, cadence, reason)

    return _closed(db_path, mutate)


def tip_check(db_path=None, day=None):
    """Decision without counting a use. Fills missing default keys when the database already exists."""
    db_path = db_path or default_db()
    try:
        today = _today(day)
    except ValueError:
        return _line(0, False, False, CADENCE_DAYS, "bad-date")

    def mutate(c):
        _ensure_defaults(c)
        uses, setup, _last_use, last_shown, cadence = _read(c)
        show, reason, cadence = evaluate(uses, setup, last_shown, cadence, today)
        return _line(uses, setup, show, cadence, reason)

    return _closed(db_path, mutate)


def mark_shown(db_path=None, day=None):
    """Call right after the card is shown. Starts the 7-day (or current) clock. Does not change cadence."""
    db_path = db_path or default_db()
    try:
        today = _today(day)
    except ValueError:
        return _line(0, False, False, CADENCE_DAYS, "bad-date")

    def mutate(c):
        _ensure_defaults(c)
        uses, setup, _last_use, last_shown, cadence = _read(c)
        if not setup:
            return _line(uses, False, False, cadence, "setup")
        _put(c, K_LAST_SHOWN, today)
        show, reason, cadence = evaluate(uses, True, today, cadence, today)
        return _line(uses, True, show, cadence, reason)

    return _closed(db_path, mutate)


def _choose(db_path, day, cadence_days):
    """Record a card response. Sets last_shown to today and the cadence. No opt-out."""
    db_path = db_path or default_db()
    try:
        today = _today(day)
    except ValueError:
        return _line(0, False, False, CADENCE_DAYS, "bad-date")

    def mutate(c):
        _ensure_defaults(c)
        uses, setup, _last_use, _last_shown, _cadence = _read(c)
        if not setup:
            return _line(uses, False, False, CADENCE_DAYS, "setup")
        _put(c, K_CADENCE, cadence_days)
        _put(c, K_LAST_SHOWN, today)
        show, reason, cadence = evaluate(uses, True, today, cadence_days, today)
        return _line(uses, True, show, cadence, reason)

    return _closed(db_path, mutate)


def mark_later(db_path=None, day=None):
    """Maybe later. Keeps the 7-day cadence so the card can show again next week."""
    return _choose(db_path, day, CADENCE_DAYS)


def mark_monthly(db_path=None, day=None):
    """Remind me monthly, or a dismiss with no button picked. Cadence becomes 30 days."""
    return _choose(db_path, day, LATER_CADENCE_DAYS)


def mark_setup_done(db_path=None):
    """End of first-run setup. Enables counting. Does not count the setup itself and never prints show=yes."""
    db_path = db_path or default_db()

    def mutate(c):
        _ensure_defaults(c, seed_uses=0, seed_last_use="", setup=False)
        _put(c, K_SETUP, "1")
        uses, _setup, _last_use, _last_shown, cadence = _read(c)
        return _line(uses, True, False, cadence, "setup-done")

    return _closed(db_path, mutate)


def _untouched(uses, last_use, last_shown, cadence):
    """Default keys only: safe to adopt historical logged days. Any real count, show, or monthly cadence is kept."""
    return uses == 0 and last_use == "" and last_shown == "" and cadence == CADENCE_DAYS


def seed_from_days(db_path=None):
    """Upgrade / imported-journal path. If the counter is still untouched, set it from logged days and mark setup complete.
    Never overwrites a counter that has already moved, a shown date, or a monthly cadence.
    The seed command itself always prints show=no so an update turn stays quiet; the next note-use decides."""
    db_path = db_path or default_db()

    def mutate(c):
        n, last = _days_stats(c)
        _ensure_defaults(c)
        uses, _setup, last_use, last_shown, cadence = _read(c)
        reason = "kept"
        if _untouched(uses, last_use, last_shown, cadence) and n > 0:
            _put(c, K_USES, n)
            _put(c, K_LAST_USE, last)
            reason = "seeded"
        _put(c, K_SETUP, "1")
        uses, setup, _last_use, _last_shown, cadence = _read(c)
        return _line(uses, setup, False, cadence, reason)

    return _closed(db_path, mutate)
