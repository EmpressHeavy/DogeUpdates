#!/usr/bin/env python3
"""Counter and cadence tests for the occasional tip prompt. Stdlib only."""
import os, sqlite3, subprocess, tempfile, time, unittest
import tip_prompt as tip

PROMPT = "Wow you seem to be using DOGE a lot lately! Would you mind sending my creator a tip? 🪙"


def init_db(path):
    env = os.environ.copy()
    env["DOGE_DB"] = path
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "doge_db.py")
    r = subprocess.run(["python3", script, "init"], env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError(r.stderr or r.stdout)


def add_days(path, dates):
    c = sqlite3.connect(path)
    for d in dates:
        c.execute(
            "insert or ignore into days(date,day_of_week,bonus_points,daily_total) values(?,?,0,0)",
            (d, "Monday"),
        )
    c.commit()
    c.close()


def cli(path, *args):
    env = os.environ.copy()
    env["DOGE_DB"] = path
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "doge_db.py")
    r = subprocess.run(["python3", script, *args], env=env, capture_output=True, text=True)
    return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()


class EvaluateTests(unittest.TestCase):
    def test_prompt_and_links_are_exact(self):
        self.assertEqual(tip.PROMPT, PROMPT)
        self.assertEqual(tip.BUTTON, "Maybe later / Remind me monthly")
        self.assertEqual(
            tip.LINKS,
            (
                ("Stripe (card)", "https://buy.stripe.com/aFacN40Mw0Arcz02VubMQ00"),
                ("Cash App", "https://cash.app/$EmpressHeavy"),
                ("Venmo", "https://venmo.com/u/EmpressHeavy"),
                ("X Money", "https://x.com/HeavyMetalShip"),
            ),
        )
        self.assertEqual(tip.X_MONEY_HANDLE, "@HeavyMetalShip")
        self.assertEqual(tip.PRIMARY_QR, "stripe.png")
        for name, filename in tip.QR_FILES.items():
            path = tip.qr_path(filename)
            with open(path, "rb") as f:
                magic = f.read(8)
            self.assertEqual(magic, b"\x89PNG\r\n\x1a\n", name)
            self.assertGreater(os.path.getsize(path), 200)

    def test_never_during_setup_even_after_many_uses(self):
        show, reason, cadence = tip.evaluate(100, False, "", 7, "2026-06-01")
        self.assertFalse(show)
        self.assertEqual(reason, "setup")
        self.assertEqual(cadence, 7)

    def test_first_show_is_at_10_uses_not_before(self):
        show, reason, _ = tip.evaluate(9, True, "", 7, "2026-06-01")
        self.assertFalse(show)
        self.assertEqual(reason, "uses")
        show, reason, _ = tip.evaluate(10, True, "", 7, "2026-06-10")
        self.assertTrue(show)
        self.assertEqual(reason, "first")

    def test_weekly_cadence_starts_after_the_first_show(self):
        shown = "2026-06-01"
        show, reason, _ = tip.evaluate(10, True, shown, 7, "2026-06-01")
        self.assertFalse(show)
        self.assertEqual(reason, "wait")
        show, reason, _ = tip.evaluate(40, True, shown, 7, "2026-06-07")
        self.assertFalse(show)
        self.assertEqual(reason, "wait")
        show, reason, cadence = tip.evaluate(40, True, shown, 7, "2026-06-08")
        self.assertTrue(show)
        self.assertEqual(reason, "due")
        self.assertEqual(cadence, 7)

    def test_maybe_later_or_dismiss_is_30_days(self):
        shown = "2026-06-01"
        show, _, cadence = tip.evaluate(20, True, shown, 30, "2026-06-08")
        self.assertFalse(show)
        self.assertEqual(cadence, 30)
        show, _, _ = tip.evaluate(20, True, shown, 30, "2026-06-30")
        self.assertFalse(show)
        show, reason, cadence = tip.evaluate(20, True, shown, 30, "2026-07-01")
        self.assertTrue(show)
        self.assertEqual(reason, "due")
        self.assertEqual(cadence, 30)

    def test_no_permanent_opt_out_value(self):
        for raw in (0, 1, 6, 7, 14, 29, 31, 365, 99999, None, "", "never", "off"):
            self.assertEqual(tip.normalize_cadence(raw), 7, raw)
        self.assertEqual(tip.normalize_cadence(30), 30)
        self.assertEqual(tip.normalize_cadence("30"), 30)
        self.assertFalse(hasattr(tip, "OPT_OUT"))
        self.assertNotIn("tip_opt_out", (tip.K_USES, tip.K_SETUP, tip.K_LAST_USE, tip.K_LAST_SHOWN, tip.K_CADENCE))


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.tmp.name, "wins.db")
        init_db(self.db)

    def tearDown(self):
        self.tmp.cleanup()

    def test_setup_days_do_not_count_or_show(self):
        for i in range(1, 16):
            line = tip.note_use(self.db, f"2026-03-{i:02d}")
            self.assertIn("show=no", line)
            self.assertIn("reason=setup", line)
            self.assertIn("uses=0", line)
        line = tip.mark_setup_done(self.db)
        self.assertIn("show=no", line)
        self.assertIn("reason=setup-done", line)
        self.assertIn("uses=0", line)

    def test_counter_reaches_first_prompt_on_the_10th_day(self):
        tip.mark_setup_done(self.db)
        for i in range(1, 10):
            line = tip.note_use(self.db, f"2026-04-{i:02d}")
            self.assertIn("show=no", line)
            self.assertIn(f"uses={i}", line)
        tenth = tip.note_use(self.db, "2026-04-10")
        self.assertEqual(tenth, "uses=10 setup=1 show=yes cadence=7 reason=first")
        again = tip.note_use(self.db, "2026-04-10")
        self.assertEqual(again, tenth)
        shown = tip.mark_shown(self.db, "2026-04-10")
        self.assertIn("show=no", shown)
        self.assertIn("cadence=7", shown)
        self.assertIn("reason=wait", shown)

    def test_same_day_is_one_use_and_does_not_touch_backup(self):
        tip.mark_setup_done(self.db)
        tip.note_use(self.db, "2026-04-01")
        tip.note_use(self.db, "2026-04-01")
        c = sqlite3.connect(self.db)
        uses, last = c.execute(
            "select value from meta where key='tip_use_count'"
        ).fetchone()[0], c.execute(
            "select value from meta where key='tip_last_use_date'"
        ).fetchone()[0]
        c.close()
        self.assertEqual(uses, "1")
        self.assertEqual(last, "2026-04-01")
        self.assertFalse(os.path.exists(os.path.join(self.tmp.name, "backup")))

    def test_weekly_then_dismiss_switches_to_monthly(self):
        tip.mark_setup_done(self.db)
        for i in range(1, 11):
            tip.note_use(self.db, f"2026-05-{i:02d}")
        tip.mark_shown(self.db, "2026-05-10")
        self.assertIn("show=no", tip.tip_check(self.db, "2026-05-16"))
        self.assertIn("show=yes", tip.tip_check(self.db, "2026-05-17"))
        self.assertIn("reason=due", tip.tip_check(self.db, "2026-05-17"))
        later = tip.mark_later(self.db, "2026-05-17")
        self.assertIn("cadence=30", later)
        self.assertIn("show=no", later)
        self.assertIn("show=no", tip.tip_check(self.db, "2026-06-15"))
        monthly = tip.tip_check(self.db, "2026-06-16")
        self.assertIn("show=yes", monthly)
        self.assertIn("cadence=30", monthly)
        self.assertIn("reason=due", monthly)

    def test_dismiss_has_no_off_switch(self):
        tip.mark_setup_done(self.db)
        for i in range(1, 11):
            tip.note_use(self.db, f"2026-08-{i:02d}")
        for _ in range(5):
            line = tip.mark_later(self.db, "2026-08-10")
            self.assertIn("cadence=30", line)
            self.assertNotIn("cadence=0", line)
        self.assertIn("show=no", tip.tip_check(self.db, "2026-09-08"))
        self.assertIn("show=yes", tip.tip_check(self.db, "2026-09-09"))
        c = sqlite3.connect(self.db)
        keys = {row[0] for row in c.execute("select key from meta")}
        c.close()
        self.assertIn("tip_cadence_days", keys)
        self.assertNotIn("tip_opt_out", keys)
        self.assertNotIn("tip_disabled", keys)

    def test_seed_counts_logged_days_without_clobbering_later_choices(self):
        add_days(self.db, [f"2026-01-{i:02d}" for i in range(1, 13)])
        seeded = tip.seed_from_days(self.db)
        self.assertIn("uses=12", seeded)
        self.assertIn("reason=seeded", seeded)
        self.assertIn("show=no", seeded)
        check = tip.tip_check(self.db, "2026-02-01")
        self.assertEqual(check, "uses=12 setup=1 show=yes cadence=7 reason=first")
        same = tip.note_use(self.db, "2026-01-12")
        self.assertIn("uses=12", same)
        nxt = tip.note_use(self.db, "2026-02-01")
        self.assertIn("uses=13", nxt)
        self.assertIn("show=yes", nxt)
        tip.mark_later(self.db, "2026-02-01")
        add_days(self.db, ["2026-02-02"])
        kept = tip.seed_from_days(self.db)
        self.assertIn("reason=kept", kept)
        self.assertIn("cadence=30", kept)
        self.assertIn("uses=13", kept)

    def test_seed_after_default_keys_still_adopts_history(self):
        add_days(self.db, [f"2025-12-{i:02d}" for i in range(1, 11)])
        early = tip.note_use(self.db, "2025-12-11")
        self.assertIn("reason=setup", early)
        self.assertIn("uses=0", early)
        seeded = tip.seed_from_days(self.db)
        self.assertIn("uses=10", seeded)
        self.assertIn("reason=seeded", seeded)
        self.assertIn("show=yes", tip.tip_check(self.db, "2025-12-20"))

    def test_missing_db_and_bad_date_do_not_raise(self):
        missing = os.path.join(self.tmp.name, "nope.db")
        self.assertIn("reason=no-db", tip.note_use(missing, "2026-01-01"))
        self.assertIn("show=no", tip.note_use(missing, "2026-01-01"))
        self.assertIn("reason=bad-date", tip.note_use(self.db, "tomorrow"))
        self.assertIn("reason=bad-date", tip.mark_later(self.db, "nope"))

    def test_note_use_stays_fast(self):
        tip.mark_setup_done(self.db)
        start = time.monotonic()
        for i in range(40):
            tip.note_use(self.db, f"2026-07-{(i % 28) + 1:02d}")
        self.assertLess(time.monotonic() - start, 2.0)

    def test_cli_matches_the_library(self):
        code, out, err = cli(self.db, "tip-setup-done")
        self.assertEqual(code, 0, err)
        self.assertIn("reason=setup-done", out)
        code, out, err = cli(self.db, "note-use", "--date", "2026-04-02")
        self.assertEqual(code, 0, err)
        self.assertEqual(out, "uses=1 setup=1 show=no cadence=7 reason=uses")
        for i in range(3, 12):
            cli(self.db, "note-use", "--date", f"2026-04-{i:02d}")
        code, out, err = cli(self.db, "tip-check", "--date", "2026-04-11")
        self.assertEqual(code, 0, err)
        self.assertIn("show=yes", out)
        self.assertIn("reason=first", out)
        code, out, err = cli(self.db, "tip-shown", "--date", "2026-04-11")
        self.assertEqual(code, 0, err)
        self.assertIn("show=no", out)
        code, out, err = cli(self.db, "tip-later", "--date", "2026-04-11")
        self.assertEqual(code, 0, err)
        self.assertIn("cadence=30", out)


if __name__ == "__main__":
    unittest.main()
