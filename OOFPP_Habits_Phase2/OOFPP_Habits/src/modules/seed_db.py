# src/modules/seed_db.py
from __future__ import annotations
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_habits.db"

def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def _dt(day: datetime, h: int = 0, m: int = 0) -> datetime:
    return day.replace(hour=h, minute=m, second=0, microsecond=0)

def _this_weekday(base: datetime, weekday_target: int, h: int, m: int) -> datetime:
    # Monday=0 ... Sunday=6
    offset = (base.weekday() - weekday_target) % 7
    return _dt(base - timedelta(days=offset), h, m)

def _ensure_dirs():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def _create_schema(cur: sqlite3.Cursor):
    cur.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS habits(
        id INTEGER PRIMARY KEY,
        name TEXT,
        periodicity TEXT,
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS completions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id INTEGER NOT NULL,
        completed_at TEXT NOT NULL,
        FOREIGN KEY(habit_id) REFERENCES habits(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_completions_habit
    ON completions (habit_id, completed_at);
    """)

def _reset(cur: sqlite3.Cursor):
    cur.execute("DELETE FROM completions;")
    cur.execute("DELETE FROM habits;")

def _insert_habits(cur: sqlite3.Cursor, created_at_iso: str):
    habits = [
        (1, "Drink Water",   "daily",   created_at_iso),
        (2, "Workout",       "weekly",  created_at_iso),
        (3, "Weekly Report", "weekly",  created_at_iso),
        (4, "House Cleaning","weekly",  created_at_iso),
        (5, "Budget Review", "monthly", created_at_iso),
    ]
    cur.executemany("INSERT INTO habits(id,name,periodicity,created_at) VALUES (?,?,?,?)", habits)

def _seed_completions(cur: sqlite3.Cursor, now: datetime):
    # Window: last two months ~ 62 days
    window_start = now - timedelta(days=62)

    # ---- (1) Daily: Drink Water (id=1) ----
    # Fill roughly the last two months with ~70% coverage, ensure a CURRENT 10-day streak.
    daily_rows = []
    # days in window (skip every 3rd day to create some misses)
    d = window_start
    k = 0
    while d.date() <= now.date():
        if k % 3 != 0:  # create some gaps earlier
            daily_rows.append((1, _iso(_dt(d, 14, 20))))
        d += timedelta(days=1)
        k += 1
    # Overwrite tail to guarantee an active 10-day streak ending today
    daily_rows = [row for row in daily_rows if datetime.fromisoformat(row[1]) < _dt(now, 0, 0)]
    for i in range(9, -1, -1):  # last 10 days incl. today
        dd = _dt(now - timedelta(days=i), 14, 20)
        daily_rows.append((1, _iso(dd)))
    cur.executemany("INSERT INTO completions(habit_id, completed_at) VALUES (?,?)", daily_rows)

    # Helper to insert recent weekly streaks (consecutive weeks including current)
    def weekly_streak(habit_id: int, weekday: int, weeks: int, h: int, m: int):
        anchor = _this_weekday(now, weekday, h, m)
        rows = []
        for w in range(weeks):
            day = anchor - timedelta(weeks=w)
            if day >= window_start:
                rows.append((habit_id, _iso(day)))
        cur.executemany("INSERT INTO completions(habit_id, completed_at) VALUES (?,?)", rows)

    # Helper to insert weekly sporadic (no current streak)
    def weekly_sporadic(habit_id: int, weekday: int, h: int, m: int, picks: list[int]):
        """picks are week offsets (0=this week, 1=last week, ...) to include."""
        anchor = _this_weekday(now, weekday, h, m)
        rows = []
        for w in picks:
            day = anchor - timedelta(weeks=w)
            if day >= window_start:
                rows.append((habit_id, _iso(day)))
        cur.executemany("INSERT INTO completions(habit_id, completed_at) VALUES (?,?)", rows)

    # ---- (2) Workout (id=2): ACTIVE weekly streak (e.g., Fridays 08:00) ----
    weekly_streak(habit_id=2, weekday=4, weeks=6, h=8, m=0)   # 6 consecutive weeks

    # ---- (3) Weekly Report (id=3): ACTIVE weekly streak (Wednesdays 14:20) ----
    weekly_streak(habit_id=3, weekday=2, weeks=5, h=14, m=20) # 5 consecutive weeks

    # ---- (4) House Cleaning (id=4): NOT a current streak (sporadic Sundays) ----
    # Choose non-consecutive weeks: e.g., 7, 5, 3 weeks ago (gap near present)
    weekly_sporadic(habit_id=4, weekday=6, h=9, m=0, picks=[7, 5, 3])

    # ---- (5) Budget Review (id=5): monthly, no current streak ----
    # Add last month's 1st and the month before's 1st, but SKIP this month's 1st if within window → breaks "current"
    first_of_now   = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # month before:
    prev_month_mid = first_of_now - timedelta(days=15)
    first_of_prev  = prev_month_mid.replace(day=1)
    # two months before:
    prev2_mid      = first_of_prev - timedelta(days=15)
    first_of_prev2 = prev2_mid.replace(day=1)

    monthly_rows = []
    for day in (first_of_prev2, first_of_prev):
        if day >= window_start:
            monthly_rows.append((5, _iso(day)))
    if monthly_rows:
        cur.executemany("INSERT INTO completions(habit_id, completed_at) VALUES (?,?)", monthly_rows)

def seed_database(db_path: Path = DB_PATH):
    _ensure_dirs()
    con = sqlite3.connect(str(db_path))
    con.execute("PRAGMA foreign_keys = ON;")
    cur = con.cursor()
    _create_schema(cur)
    _reset(cur)

    now = datetime.now()
    created_at_iso = _iso(now - timedelta(days=70))
    _insert_habits(cur, created_at_iso)
    _seed_completions(cur, now)

    con.commit()
    con.close()
    return db_path

def seed_if_needed():
    """
    Run this at app start:
    - If DB missing or empty, seed it.
    - If DB exists and has data, leave it alone.
    """
    if not DB_PATH.exists():
        seed_database()
        return

    con = sqlite3.connect(str(DB_PATH))
    try:
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM habits;")
        habits_count = cur.fetchone()[0]
        if habits_count == 0:
            seed_database()
    finally:
        con.close()

if __name__ == "__main__":
    path = seed_database()
    print(f"Seeded sample data into {path}")

