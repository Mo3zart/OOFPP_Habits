""" habit module for the Habit Tracker application.

Moritz Zewinger - OOFPP – DLBDSOOFPP01

This module is part of the student portfolio submission."""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

VALID_PERIODICITIES = {"daily", "weekly", "monthly"}


@dataclass
class Habit:
    """
    Domain model for a Habit.

    Attributes:
        id: Optional integer id assigned by the DB (None until persisted).
        name: The habit name.
        periodicity: One of VALID_PERIODICITIES.
        created_at: UTC datetime when the habit was created.
        completions: list of UTC datetimes when this habit was completed.
    """
    id: Optional[int]
    name: str
    periodicity: str
    created_at: datetime = field(default_factory=lambda: datetime.utcnow())
    completions: List[datetime] = field(default_factory=list)

    def __post_init__(self) -> None:
        """  post init  .

        Moritz Zewinger - OOFPP – DLBDSOOFPP01

        Args:
            None

        Returns:
            None
        """

        if self.periodicity not in VALID_PERIODICITIES:
            raise ValueError(f"Invalid periodicity '{self.periodicity}'. Valid: {sorted(VALID_PERIODICITIES)}")

    def to_db_row(self) -> tuple:
        """
        Return a tuple suitable for inserting/updating the habits table
        (name, periodicity, created_at_iso).
        """
        return (self.name, self.periodicity, self.created_at.isoformat())

    @staticmethod
    def from_db_row(row: tuple, completions: Optional[List[datetime]] = None) -> "Habit":
        """
        Create Habit from a DB row and optional completions list.
        Expect row: (id, name, periodicity, created_at_iso).
        """
        hid, name, periodicity, created_at_iso = row
        created_at = datetime.fromisoformat(created_at_iso)
        return Habit(id=hid, name=name, periodicity=periodicity, created_at=created_at,
                     completions=completions or [])

    def add_completion(self, when: Optional[datetime] = None) -> None:
        """Append a completion timestamp (in-memory). Persistence happens via StorageHandler."""
        self.completions.append(when or datetime.utcnow())
