create table days(date text primary key, day_of_week text, quests_done text, bonus_points real, daily_total real, notes text);
create table wins(date text, idx integer, text text, primary key(date,idx));
create table quests(date text, text text, done integer default 0, carried_to text, status text);
create table money(platform text, amount real, date text, status text, notes text);
create table goals(goal text, type text, target real, progress real, start_date text, target_date text, notes text, percent_done text);
create table log_archive(date text, type text, item text, notes text);
create table spending_categories(category text, amount real, pct_of_total text);
create table spending_transactions(date text, merchant text, category text, amount real, account text);
create table meta(key text primary key, value text);
-- Tip prompt (v12) uses meta only, no new table: tip_use_count, tip_setup_complete,
-- tip_last_use_date, tip_last_shown, tip_cadence_days (7, or 30 after "maybe later" / dismiss).
