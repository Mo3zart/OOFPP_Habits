"""
Unit tests for analytics.py.

Covers:
- _period_delta() correctness
- calculate_streaks() daily/weekly/monthly logic
- list_all_habits(), list_by_periodicity()
- longest_streak_for_habit(), longest_streak_overall(), longest_streak_for_habit_name()
"""
import pytest
from datetime import datetime, timedelta

from src.modules import analytics
from src.modules.habit import Habit


def _make_habit(name: str, periodicity: str, completions: list[datetime]):
    return Habit(id=None, name=name, periodicity=periodicity, completions=completions)


# ----------------------------------------------------------------------
# _period_delta
# ----------------------------------------------------------------------

@pytest.mark.parametrize("periodicity,expected_days", [
    ("daily", 1),
    ("weekly", 7),
    ("monthly", 30),
])
def test_period_delta_valid(periodicity, expected_days):
    delta = analytics._period_delta(periodicity)
    assert isinstance(delta, timedelta)
    assert delta.days == expected_days


def test_period_delta_invalid():
    with pytest.raises(ValueError):
        analytics._period_delta("yearly")


# ----------------------------------------------------------------------
# calculate_streaks
# ----------------------------------------------------------------------

def test_calculate_streaks_empty_returns_zero():
    h = _make_habit("Empty", "daily", [])
    assert analytics.calculate_streaks(h) == 0


def test_calculate_streaks_daily_continuous():
    now = datetime.utcnow()
    completions = [now - timedelta(days=i) for i in range(3)]
    h = _make_habit("Drink Water", "daily", completions[::-1])
    streak = analytics.calculate_streaks(h)
    assert isinstance(streak, int)
    assert streak >= 1


def test_calculate_streaks_broken_sequence():
    now = datetime.utcnow()
    completions = [now - timedelta(days=i * 3) for i in range(3)]  # too far apart
    h = _make_habit("Workout", "daily", completions[::-1])
    streak = analytics.calculate_streaks(h)
    assert streak <= 1


# ----------------------------------------------------------------------
# list_all_habits / list_by_periodicity
# ----------------------------------------------------------------------

def test_list_all_habits_and_by_periodicity():
    habits = [
        _make_habit("Water", "daily", []),
        _make_habit("Workout", "weekly", []),
        _make_habit("Budget", "monthly", []),
    ]
    all_names = analytics.list_all_habits(habits)
    assert all_names == ["Water", "Workout", "Budget"]

    weekly = analytics.list_by_periodicity(habits, "weekly")
    assert len(weekly) == 1 and weekly[0].name == "Workout"


# ----------------------------------------------------------------------
# longest_streak_* functions
# ----------------------------------------------------------------------

def test_longest_streak_for_habit_and_name():
    now = datetime.utcnow()
    h = _make_habit("Test", "daily", [now - timedelta(days=i) for i in range(5)])
    val1 = analytics.longest_streak_for_habit(h)
    val2 = analytics.longest_streak_for_habit_name([h], "test")
    assert val1 == val2
    assert isinstance(val1, int)


def test_longest_streak_overall():
    now = datetime.utcnow()
    habits = [
        _make_habit("Water", "daily", [now - timedelta(days=i) for i in range(5)]),
        _make_habit("Workout", "weekly", [now - timedelta(weeks=i) for i in range(3)]),
    ]
    result = analytics.longest_streak_overall(habits)
    assert isinstance(result, tuple)
    name, streak = result
    assert name in ("Water", "Workout")
    assert isinstance(streak, int)
