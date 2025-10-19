import sqlite3
import os
from .storage_handler import StorageHandler
from datetime import datetime

class SQLiteHandler(StorageHandler):
    def __init__(self, db_path="data/habits.db"):
        self.db_path = db_path or os.getenv("DB_PATH", "/app/src/data/habits.db")
        self._connect()

    def _connect(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY,
                name TEXT,
                periodicity TEXT,
                created_at TEXT

            )
        """)
        self.conn.commit()

    def update(self, habit_id, new_name=None, new_periodicity=None):
        """Update a habit's name or periodicity by its ID."""
        if not new_name and not new_periodicity:
            return False  # nothing to update

        # Build the dynamic SQL update query
        fields = []
        values = []

        if new_name:
            fields.append("name = ?")
            values.append(new_name)
        if new_periodicity:
            fields.append("periodicity = ?")
            values.append(new_periodicity)

        values.append(habit_id)
        sql = f"UPDATE habits SET {', '.join(fields)} WHERE id = ?"

        self.cursor.execute(sql, tuple(values))
        self.conn.commit()

        return self.cursor.rowcount > 0


    def save(self, habit):
        self.cursor.execute(
            "INSERT INTO habits (name, periodicity, created_at) VALUES (?, ?, ?)",
            (habit.name, habit.periodicity, habit.created_at.isoformat())
        )
        self.conn.commit()

    def get_by_id(self, habit_id):
        self.cursor.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
        return self.cursor.fetchone()

    def load(self):
        self.cursor.execute("SELECT * FROM habits ORDER BY id DESC")
        return self.cursor.fetchall()

    def delete(self, habit_id):
        """Delete habit by ID."""
        self.cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        self.conn.commit()

        if self.cursor.rowcount == 0: 
            return False
        return True
