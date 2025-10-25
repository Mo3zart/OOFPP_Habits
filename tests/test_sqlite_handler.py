"""
Unit tests for SQLiteHandler.

This verifies:
- habit insertion/update/delete using SQL and class methods
- completion add/retrieve logic
- context manager functionality
"""
import sqlite3
from datetime import datetime, timedelta
import pytest

from src.modules.sqlite_handler import SQLiteHandler


@pytest.fixture
def db_handler(tmp_path):
    """Provide a SQLiteHandler with an isolated temporary DB file."""
    db_file = tmp_path / "test_habits.db"
    conn = sqlite3.connect(db_file)
    conn.executescript("""
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
    """)
    conn.commit()
    handler = SQLiteHandler(db_file)
    handler.conn = conn
    yield handler
    handler.close()


def test_add_and_get_completions(db_handler):
    """Verify add_completion() and get_completions() integration."""
    cur = db_handler.conn.cursor()
    cur.execute("INSERT INTO habits (id, name, periodicity, created_at) VALUES (1, 'Water', 'daily', ?);",
                (datetime.utcnow().isoformat(),))
    db_handler.conn.commit()

    now = datetime(2025, 10, 25, 12, 0)
    ok = db_handler.add_completion(1, now)
    assert ok

    comps = db_handler.get_completions(1)
    assert isinstance(comps, list)
    assert comps and isinstance(comps[0], datetime)


def test_update_and_delete_habit(db_handler):
    """Ensure update_habit() and delete_habit() modify the database correctly."""
    cur = db_handler.conn.cursor()
    cur.execute("INSERT INTO habits (id, name, periodicity, created_at) VALUES (1, 'Old', 'daily', ?);",
                (datetime.utcnow().isoformat(),))
    db_handler.conn.commit()

    updated = db_handler.update_habit(1, name="NewName", periodicity="weekly")
    assert updated
    cur.execute("SELECT name, periodicity FROM habits WHERE id = 1;")
    name, per = cur.fetchone()
    assert name == "NewName"
    assert per == "weekly"

    deleted = db_handler.delete_habit(1)
    assert deleted
    cur.execute("SELECT COUNT(*) FROM habits;")
    assert cur.fetchone()[0] == 0


def test_get_all_completions_returns_joined_rows(db_handler):
    """get_all_completions() should join habit and completion data."""
    cur = db_handler.conn.cursor()
    cur.execute("INSERT INTO habits (id, name, periodicity, created_at) VALUES (1, 'Work', 'weekly', ?);",
                (datetime.utcnow().isoformat(),))
    cur.execute("INSERT INTO completions (habit_id, completed_at) VALUES (1, ?);",
                (datetime.utcnow().isoformat(),))
    db_handler.conn.commit()

    rows = db_handler.get_all_completions()
    assert isinstance(rows, list)
    assert all(len(r) == 3 for r in rows)
    assert rows[0][1] == "Work"


def test_context_manager_support(tmp_path):
    """SQLiteHandler should support context manager (with-statement)."""
    db_file = tmp_path / "context.db"
    handler = SQLiteHandler(db_file)
    with handler as h:
        assert isinstance(h, SQLiteHandler)
        assert hasattr(h, "conn")
    with pytest.raises(sqlite3.ProgrammingError):
        h.conn.execute("SELECT 1;")
