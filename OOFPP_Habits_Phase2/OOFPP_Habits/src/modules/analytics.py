""" analytics module for the Habit Tracker application.

Moritz Zewinger - OOFPP – DLBDSOOFPP01

This module is part of the student portfolio submission."""

# src/modules/analytics.py
from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from .habit import Habit


def _period_delta(periodicity: str) -> timedelta:
    """Return a timedelta that represents the period length."""
    if periodicity == "daily":
        return timedelta(days=1)
    elif periodicity == "weekly":
        return timedelta(weeks=1)
    elif periodicity == "monthly":
        return timedelta(days=30)
    else:
        raise ValueError(f"Unsupported periodicity: {periodicity}")


def calculate_streaks(habit: Habit) -> int:
    """
    Calculate the *current active streak* for a habit.
    A streak continues only if completions fall within the expected timeframes,
    and it resets if the habit was missed recently.
    """
    completions = sorted(habit.completions)
    if not completions:
        return 0

    period = _period_delta(habit.periodicity)
    now = datetime.utcnow()

    # Check if the last completion is still "recent enough" for this period.
    #    If too long ago, the streak is considered broken.
    if (now - completions[-1]) > (period + timedelta(hours=12)):
        return 0

    streak = 1
    for i in range(len(completions) - 2, -1, -1):
        delta = completions[i + 1] - completions[i]
        if delta <= period + timedelta(hours=12):
            streak += 1
        else:
            break
    return streak

# ------------------------------
# Analytics API
# ------------------------------


def list_all_habits(habits: List[Habit]) -> List[str]:
    """Return a list of all habit names."""
    return list(map(lambda h: h.name, habits))


def list_by_periodicity(habits: List[Habit], periodicity: str) -> List[Habit]:
    """Return habits matching a given periodicity."""
    return list(filter(lambda h: h.periodicity == periodicity, habits))


def longest_streak_for_habit(habit: Habit) -> int:
    """Return the longest streak for a specific habit."""
    return calculate_streaks(habit)


def longest_streak_overall(habits: List[Habit]) -> Optional[Dict[str, int]]:
    """Return the habit with the longest streak among all."""
    if not habits:
        return None

    streaks = list(map(lambda h: (h.name, calculate_streaks(h)), habits))
    return max(streaks, key=lambda x: x[1]) if streaks else None


def longest_streak_for_habit_name(habits: List[Habit], name: str) -> Optional[int]:
    """
    Return the longest streak for a habit given its name.
    Case-insensitive name matching.
    """
    for h in habits:
        if h.name.lower() == name.lower():
            return calculate_streaks(h)
    return None
