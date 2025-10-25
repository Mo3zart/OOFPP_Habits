from __future__ import annotations
import sqlite3
from datetime import datetime
from typing import List, Optional
from .storage_handler import StorageHandler
from .habit import Habit


_DEFAULT_TIMEOUT = 5.0


class SQLiteHandler(StorageHandler):
    """
    SQLite-based implementation of StorageHandler.

    Stores:
      - habits (id, name, periodicity, created_at)
      - completions (id, habit_id, completed_at)
    """

    def __init__(self, db_path: str = "src/data/sample_habits.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, timeout=_DEFAULT_TIMEOUT, check_same_thread=False)
        # Return rows as tuples (default)
        self._ensure_pragmas()
        self.ensure_tables()

    def _ensure_pragmas(self) -> None:
        # enable foreign keys (important for cascade deletes)
        cur = self.conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON;")
        cur.close()

    def ensure_tables(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                periodicity TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                completed_at TEXT NOT NULL,
                FOREIGN KEY(habit_id) REFERENCES habits(id) ON DELETE CASCADE
            );
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_completions_habit ON completions (habit_id, completed_at);")
        self.conn.commit()
        cur.close()

    # -------------------------
    # Habit CRUD implementations
    # -------------------------
    def save_habit(self, habit: Habit) -> int:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO habits (name, periodicity, created_at) VALUES (?, ?, ?);",
            (habit.name, habit.periodicity, habit.created_at.isoformat()),
        )
        self.conn.commit()
        hid = cur.lastrowid
        cur.close()
        return hid

    def load_habits(self) -> List[Habit]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, periodicity, created_at FROM habits ORDER BY id;")
        rows = cur.fetchall()
        habits: List[Habit] = []
        for row in rows:
            hid = row[0]
            completions = self.get_completions(hid)
            habits.append(Habit.from_db_row(row, completions=completions))
        cur.close()
        return habits

    def get_habit_by_id(self, habit_id: int) -> Optional[Habit]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, periodicity, created_at FROM habits WHERE id = ?;", (habit_id,))
        row = cur.fetchone()
        cur.close()
        if row is None:
            return None
        completions = self.get_completions(row[0])
        return Habit.from_db_row(row, completions=completions)

    def update_habit(self, habit_id: int, **fields) -> bool:
        allowed = {"name", "periodicity"}
        to_update = {k: v for k, v in fields.items() if k in allowed and v is not None}
        if not to_update:
            return False
        set_clause = ", ".join(f"{k} = ?" for k in to_update.keys())
        params = list(to_update.values()) + [habit_id]
        cur = self.conn.cursor()
        cur.execute(f"UPDATE habits SET {set_clause} WHERE id = ?;", tuple(params))
        self.conn.commit()
        updated = cur.rowcount > 0
        cur.close()
        return updated

    def delete_habit(self, habit_id: int) -> bool:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM habits WHERE id = ?;", (habit_id,))
        self.conn.commit()
        deleted = cur.rowcount > 0
        cur.close()
        return deleted

    # -------------------------
    # Completions implementations
    # -------------------------
    def add_completion(self, habit_id: int, when: datetime) -> bool:
        cur = self.conn.cursor()
        cur.execute("INSERT INTO completions (habit_id, completed_at) VALUES (?, ?);", (habit_id, when.isoformat()))
        self.conn.commit()
        inserted = cur.lastrowid is not None
        cur.close()
        return inserted

    def get_completions(self, habit_id: int) -> List[datetime]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT completed_at FROM completions WHERE habit_id = ? ORDER BY completed_at ASC;", (habit_id,)
        )
        rows = cur.fetchall()
        cur.close()
        # convert ISO strings to datetimes
        return [datetime.fromisoformat(r[0]) for r in rows]

    def get_all_completions(self) -> list[tuple[int, str, str]]:
        """Return all completions joined with their habit names."""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT c.habit_id, h.name, c.completed_at
            FROM completions AS c
            JOIN habits AS h ON c.habit_id = h.id
            ORDER BY c.completed_at DESC
        """)
        rows = cur.fetchall()
        cur.close()
        return rows

    # -------------------------
    # Close/cleanup
    # -------------------------
    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass

    # Support context manager usage if desired
    def __enter__(self) -> "SQLiteHandler":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

