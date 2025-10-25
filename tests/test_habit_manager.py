"""
Unit tests for HabitManager.

Mock the StorageHandler to verify correct delegation and logic flow.
"""
from datetime import datetime, timedelta
import pytest

from src.modules.habit_manager import HabitManager
from src.modules.habit import Habit


class DummyStorage:
    """Simple in-memory storage mock for HabitManager tests."""
    def __init__(self):
        self.habits = {}
        self.completions = {}
        self.next_id = 1
        self.tables_ensured = False

    def ensure_tables(self):
        self.tables_ensured = True

    # CRUD
    def save_habit(self, habit: Habit) -> int:
        habit.id = self.next_id
        self.habits[self.next_id] = habit
        self.next_id += 1
        return habit.id

    def load_habits(self):
        return list(self.habits.values())

    def get_habit_by_id(self, hid):
        return self.habits.get(hid)

    def update_habit(self, hid, **fields):
        if hid not in self.habits:
            return False
        for k, v in fields.items():
            if v is not None:
                setattr(self.habits[hid], k, v)
        return True

    def delete_habit(self, hid):
        return self.habits.pop(hid, None) is not None

    # Completions
    def add_completion(self, hid, when):
        if hid not in self.habits:
            return False
        self.completions.setdefault(hid, []).append(when)
        self.habits[hid].completions.append(when)
        return True

    def get_completions(self, hid):
        return self.completions.get(hid, [])


@pytest.fixture
def manager():
    return HabitManager(DummyStorage())


def test_ensure_tables_called_on_init():
    store = DummyStorage()
    HabitManager(store)
    assert store.tables_ensured is True


def test_create_and_get_habit(manager):
    h = manager.create_habit("Drink Water", "daily")
    assert isinstance(h, Habit)
    assert h.name == "Drink Water"
    fetched = manager.get_habit(h.id)
    assert fetched is not None
    assert fetched.name == "Drink Water"


def test_list_habits_returns_all(manager):
    manager.create_habit("Workout", "weekly")
    manager.create_habit("Budget Review", "monthly")
    habits = manager.list_habits()
    assert len(habits) == 2
    assert all(isinstance(h, Habit) for h in habits)


def test_update_and_delete_habit(manager):
    h = manager.create_habit("Read", "daily")
    ok = manager.update_habit(h.id, name="Study", periodicity="weekly")
    assert ok
    updated = manager.get_habit(h.id)
    assert updated.name == "Study"
    assert updated.periodicity == "weekly"
    deleted = manager.delete_habit(h.id)
    assert deleted
    assert manager.get_habit(h.id) is None


def test_complete_habit_success_and_failure(manager):
    h = manager.create_habit("Exercise", "weekly")
    ts = datetime(2025, 10, 25, 10, 0)
    ok = manager.complete_habit(h.id, ts)
    assert ok
    # Completions should be stored
    comps = manager.storage.get_completions(h.id)
    assert ts in comps

    # Invalid habit id should fail gracefully
    assert manager.complete_habit(999) is False


def test_latest_completion_returns_recent(manager):
    h = manager.create_habit("Test", "daily")
    now = datetime.utcnow()
    earlier = now - timedelta(days=1)
    manager.complete_habit(h.id, earlier)
    manager.complete_habit(h.id, now)
    latest = manager.latest_completion(h.id)
    assert latest == max(h.completions)
