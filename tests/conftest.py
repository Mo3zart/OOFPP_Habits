"""
Pytest configuration & shared fixtures for the Habit Tracker project.

This file provides:
- Reliable imports from the project (adds repository root to sys.path).
- An in-memory SQLite database that mirrors your production schema.
- Optional sample data to re-use across tests.
"""
from __future__ import annotations

import os
import sys
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import pytest


# --- Make "src" importable without modifying the app code --------------------
_REPO_ROOT = Path(__file__).resolve().parents[1]
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


# --- DB schema (mirrors sample_habits.db) -------------
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS habits(
    id INTEGER PRIMARY KEY,
    name TEXT,
    periodicity TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    completed_at TEXT NOT NULL,
    FOREIGN KEY(habit_id) REFERENCES habits(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_completions_habit ON completions (habit_id, completed_at);
"""


@pytest.fixture(scope="session")
def sqlite_memory_conn():
    """
    Session-scoped in-memory SQLite connection with the project schema.
    Use this for fast, isolated tests that touch persistence.
    """
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA_SQL)
    yield conn
    conn.close()


@pytest.fixture
def fresh_db(sqlite_memory_conn):
    """
    Function-scoped clean database.
    We wrap the session connection in a SAVEPOINT and roll back after each test,
    so schema is kept but data is isolated.
    """
    conn = sqlite_memory_conn
    conn.execute("SAVEPOINT fresh_case;")
    try:
        yield conn
    finally:
        conn.execute("ROLLBACK TO fresh_case;")
        conn.execute("RELEASE fresh_case;")


# --- Optional: sample data builders -------------------------------------------

@dataclass
class HabitSeed:
    id: int
    name: str
    periodicity: str  # "daily" | "weekly" | "monthly"
    created_at: datetime


def _insert_habit(conn: sqlite3.Connection, seed: HabitSeed) -> None:
    conn.execute(
        "INSERT INTO habits (id, name, periodicity, created_at) VALUES (?, ?, ?, ?)",
        (seed.id, seed.name, seed.periodicity, seed.created_at.isoformat(timespec="seconds")),
    )


def _insert_completion(conn: sqlite3.Connection, habit_id: int, when: datetime) -> None:
    conn.execute(
        "INSERT INTO completions (habit_id, completed_at) VALUES (?, ?)",
        (habit_id, when.isoformat(timespec="seconds")),
    )


@pytest.fixture
def sample_data(fresh_db):
    """
    Populates the DB with 5 habits (mix of daily/weekly) and 4 weeks of example
    completions. Designed to cover streak and edge cases.

    Returns the connection for convenience.
    """
    now = datetime(2025, 10, 25, 12, 0, 0)
    habits = [
        HabitSeed(1, "Drink Water", "daily",   now - timedelta(days=40)),
        HabitSeed(2, "Workout",     "weekly",  now - timedelta(days=60)),
        HabitSeed(3, "Weekly Report","weekly", now - timedelta(days=35)),
        HabitSeed(4, "House Cleaning","weekly",now - timedelta(days=60)),
        HabitSeed(5, "Budget Review","monthly",now - timedelta(days=60)), 
    ]

    for h in habits:
        _insert_habit(fresh_db, h)

    # Daily habit: 20-day streak ending yesterday
    for d in range(1, 21):
        _insert_completion(fresh_db, 1, now - timedelta(days=d))

    # Weekly habit: 4 consecutive weeks (one per week on Mondays)
    for w in range(4):
        _insert_completion(fresh_db, 2, (now - timedelta(weeks=w)).replace(hour=9, minute=0))

    # Weekly report: 5-of-6 weeks with one gap to simulate a broken streak
    for w in [0, 1, 2, 4, 5]:
        _insert_completion(fresh_db, 3, (now - timedelta(weeks=w)).replace(hour=14, minute=20))

    # House cleaning: 2 completions one week apart
    _insert_completion(fresh_db, 4, now - timedelta(weeks=7))
    _insert_completion(fresh_db, 4, now - timedelta(weeks=6))

    # Budget review (monthly): two months
    _insert_completion(fresh_db, 5, now - timedelta(days=55))
    _insert_completion(fresh_db, 5, now - timedelta(days=25))

    fresh_db.commit()
    return fresh_db


# --- Utility marker to gracefully skip when symbols are missing ----------------
def require_attrs(module, *attrs):
    """
    Helper: returns a pytest.skip if an attribute is missing on a module.
    Use in tests like:
        require_attrs(analytics, "longest_streak")
    """
    missing = [a for a in attrs if not hasattr(module, a)]
    if missing:
        pytest.skip(f"Missing expected attribute(s) on {module.__name__}: {', '.join(missing)}")
    return True
