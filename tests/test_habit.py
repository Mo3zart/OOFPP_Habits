"""
Unit tests for the Habit dataclass.

This verifies:
- correct initialization of dataclass fields
- adding completions via add_completion()
- conversion to/from database rows (to_db_row / from_db_row)
- equality and representation consistency
"""
from datetime import datetime

from src.modules.habit import Habit


def test_habit_initialization_defaults():
    """Ensure default fields like created_at and completions initialize properly."""
    h = Habit(id=None, name="Drink Water", periodicity="daily")
    assert h.id is None
    assert h.name == "Drink Water"
    assert h.periodicity == "daily"
    assert isinstance(h.created_at, datetime)
    assert isinstance(h.completions, list)
    assert len(h.completions) == 0


def test_add_completion_appends_timestamp():
    """Adding a completion should increase completions list length."""
    h = Habit(id=1, name="Workout", periodicity="weekly")
    before = len(h.completions)
    now = datetime(2025, 10, 25, 9, 0)
    h.add_completion(now)
    assert len(h.completions) == before + 1
    assert h.completions[-1] == now


def test_to_db_row_and_from_db_row_roundtrip():
    """Habit should serialize to and from DB row consistently."""
    h = Habit(id=10, name="Read", periodicity="daily", created_at=datetime(2025, 10, 20))
    db_row = h.to_db_row()
    assert isinstance(db_row, tuple)
    if len(db_row) == 3:
        name, periodicity, created_at = db_row
        db_row = (10, name, periodicity, created_at)
    restored = Habit.from_db_row(db_row)
    assert restored.name == h.name
    assert restored.periodicity == h.periodicity
    assert isinstance(restored.created_at, datetime)


def test_repr_and_equality_consistency():
    """__repr__ and __eq__ should behave as dataclass defaults."""
    now = datetime(2025, 10, 25, 15, 30, 20)
    h1 = Habit(id=1, name="Budget Review", periodicity="monthly", created_at=now)
    h2 = Habit(id=1, name="Budget Review", periodicity="monthly", created_at=now)
    h3 = Habit(id=2, name="Workout", periodicity="weekly", created_at=now)

    assert repr(h1)
    assert h1 == h2
    assert h1 != h3

