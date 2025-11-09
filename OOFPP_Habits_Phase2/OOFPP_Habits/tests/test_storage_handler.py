"""
Unit tests for the abstract StorageHandler class.

These tests verify:
- Abstract base class behavior (cannot instantiate directly)
- Presence of all required abstract methods
- Instantiability and behavior of a minimal concrete subclass
"""
import pytest
from datetime import datetime

from src.modules.storage_handler import StorageHandler
from src.modules.habit import Habit


def test_storage_handler_is_abstract():
    """Attempting to instantiate StorageHandler directly should raise TypeError."""
    with pytest.raises(TypeError):
        StorageHandler()


def test_expected_abstract_methods_exist():
    """Ensure all required abstract methods are defined."""
    expected = {
        "ensure_tables", "save_habit", "load_habits", "get_habit_by_id",
        "update_habit", "delete_habit", "add_completion", "get_completions"
    }
    actual = {name for name in dir(StorageHandler) if not name.startswith("_")}
    for name in expected:
        assert name in actual, f"Missing method: {name}"


class DummyStorage(StorageHandler):
    """Minimal concrete implementation for testing."""
    def __init__(self):
        self.habits = {}
        self.completions = {}

    def ensure_tables(self): return True
    def save_habit(self, habit: Habit) -> int:
        hid = len(self.habits) + 1
        habit.id = hid
        self.habits[hid] = habit
        return hid

    def load_habits(self): return list(self.habits.values())
    def get_habit_by_id(self, habit_id): return self.habits.get(habit_id)
    def update_habit(self, habit_id, **fields):
        if habit_id not in self.habits: return False
        for k, v in fields.items():
            if v is not None: setattr(self.habits[habit_id], k, v)
        return True
    def delete_habit(self, habit_id):
        return self.habits.pop(habit_id, None) is not None
    def add_completion(self, habit_id, when: datetime):
        self.completions.setdefault(habit_id, []).append(when)
        return True
    def get_completions(self, habit_id):
        return self.completions.get(habit_id, [])


@pytest.fixture
def dummy_storage():
    return DummyStorage()


def test_concrete_subclass_can_be_instantiated(dummy_storage):
    """DummyStorage should be instantiable and usable."""
    assert isinstance(dummy_storage, StorageHandler)
    habit = Habit(id=None, name="Drink Water", periodicity="daily")
    hid = dummy_storage.save_habit(habit)
    assert hid == 1
    assert dummy_storage.get_habit_by_id(hid).name == "Drink Water"


def test_crud_and_completions(dummy_storage):
    """Test the full lifecycle using DummyStorage."""
    h = Habit(id=None, name="Workout", periodicity="weekly")
    hid = dummy_storage.save_habit(h)
    dummy_storage.update_habit(hid, name="Updated")
    updated = dummy_storage.get_habit_by_id(hid)
    assert updated.name == "Updated"

    now = datetime.utcnow()
    dummy_storage.add_completion(hid, now)
    comps = dummy_storage.get_completions(hid)
    assert comps == [now]

    deleted = dummy_storage.delete_habit(hid)
    assert deleted
    assert dummy_storage.get_habit_by_id(hid) is None
