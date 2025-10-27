""" habit_manager module for the Habit Tracker application.

Moritz Zewinger - OOFPP – DLBDSOOFPP01

This module is part of the student portfolio submission."""

from __future__ import annotations
from datetime import datetime
from typing import List, Optional

from .storage_handler import StorageHandler
from .habit import Habit


class HabitManager:
    """
    Service layer for habit operations.

    This layer contains domain logic and delegates persistence to the injected StorageHandler.
    """

    def __init__(self, storage: StorageHandler):
        """  init  .

        Moritz Zewinger - OOFPP – DLBDSOOFPP01

        Args:
            storage: Description.

        Returns:
            None
        """

        self.storage = storage
        # ensure DB schema exists
        self.storage.ensure_tables()

    # -------------------------
    # CRUD operations
    # -------------------------
    def create_habit(self, name: str, periodicity: str) -> Habit:
        """
        Create and persist a new habit. Returns the Habit (with id set).
        """
        habit = Habit(id=None, name=name, periodicity=periodicity, created_at=datetime.utcnow())
        hid = self.storage.save_habit(habit)
        return self.get_habit(hid)

    def list_habits(self) -> List[Habit]:
        """Return all habits (with completions)."""
        return self.storage.load_habits()

    def get_habit(self, habit_id: int) -> Optional[Habit]:
        """Return habit by id or None."""
        return self.storage.get_habit_by_id(habit_id)

    def update_habit(self, habit_id: int, *, name: Optional[str] = None, periodicity: Optional[str] = None) -> bool:
        """Update habit fields. Return True if updated."""
        return self.storage.update_habit(habit_id, name=name, periodicity=periodicity)

    def delete_habit(self, habit_id: int) -> bool:
        """Delete habit and its completions."""
        return self.storage.delete_habit(habit_id)

    # -------------------------
    # Completion operations
    # -------------------------
    def complete_habit(self, habit_id: int, when: Optional[datetime] = None) -> bool:
        """
        Mark a habit as completed at `when` (UTC). If when is None, uses datetime.utcnow().
        Returns True on success, False if habit not found.
        """
        habit = self.get_habit(habit_id)
        if habit is None:
            return False
        ts = when or datetime.utcnow()
        ok = self.storage.add_completion(habit_id, ts)
        return bool(ok)

    # -------------------------
    # Convenience helpers
    # -------------------------
    def latest_completion(self, habit_id: int) -> Optional[datetime]:
        """Latest completion.

        Moritz Zewinger - OOFPP – DLBDSOOFPP01

        Args:
            habit_id: Description.

        Returns:
            None
        """

        habit = self.get_habit(habit_id)
        if habit and habit.completions:
            return max(habit.completions)
        return None
