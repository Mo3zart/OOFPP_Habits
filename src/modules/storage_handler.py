""" storage_handler module for the Habit Tracker application.

Moritz Zewinger - OOFPP – DLBDSOOFPP01

This module is part of the student portfolio submission."""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from .habit import Habit


class StorageHandler(ABC):
    """Abstract storage interface for habit persistence and completions."""

    @abstractmethod
    def ensure_tables(self) -> None:
        """Create DB tables if they don't exist."""
        raise NotImplementedError

    # Habit CRUD
    @abstractmethod
    def save_habit(self, habit: Habit) -> int:
        """Save a new habit, return the assigned id."""
        raise NotImplementedError

    @abstractmethod
    def load_habits(self) -> List[Habit]:
        """Load all habits (including completions)."""
        raise NotImplementedError

    @abstractmethod
    def get_habit_by_id(self, habit_id: int) -> Optional[Habit]:
        """Return Habit or None."""
        raise NotImplementedError

    @abstractmethod
    def update_habit(self, habit_id: int, **fields) -> bool:
        """Update habit fields (name, periodicity). Return True if updated."""
        raise NotImplementedError

    @abstractmethod
    def delete_habit(self, habit_id: int) -> bool:
        """Delete a habit and its completions. Return True if deleted."""
        raise NotImplementedError

    # Completions
    @abstractmethod
    def add_completion(self, habit_id: int, when: datetime) -> bool:
        """Record a completion for a habit. Return True on success."""
        raise NotImplementedError

    @abstractmethod
    def get_completions(self, habit_id: int) -> List[datetime]:
        """Return completion datetimes for a habit (UTC)."""
        raise NotImplementedError
