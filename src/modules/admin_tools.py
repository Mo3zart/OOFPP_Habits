# src/modules/admin_tools.py
from __future__ import annotations
from datetime import datetime, timedelta
from random import random
from typing import List
from .habit import Habit
from .habit_manager import HabitManager


def seed_dummy_habits(manager: HabitManager) -> List[Habit]:
    """
    Create a list of dummy habits for testing and analytics demonstration.
    Only creates habits that do not already exist (by name).
    """
    dummy_data = [
        ("Drink Water", "daily"),
        ("Workout", "daily"),
        ("Weekly Report", "weekly"),
        ("House Cleaning", "weekly"),
        ("Budget Review", "monthly"),
    ]

    existing = {h.name.lower() for h in manager.list_habits()}
    habits = []

    for name, periodicity in dummy_data:
        if name.lower() not in existing:
            habit = manager.create_habit(name, periodicity)
            habits.append(habit)

    return habits


def add_fake_completions(manager: HabitManager, span_days: int = 90) -> None:
    """
    Populate fake completion data for all habits, simulating realistic patterns.
    - Daily habits: mostly complete, some missed days
    - Weekly habits: sometimes skip a week
    - Monthly habits: occasional misses
    """

    habits = manager.list_habits()
    now = datetime.utcnow()

    for h in habits:
        periodicity = h.periodicity.lower()

        if periodicity == "daily":
            delta = timedelta(days=1)
            num_iterations = span_days
            miss_chance = 0.2  # 20% chance to skip a day

        elif periodicity == "weekly":
            delta = timedelta(weeks=1)
            num_iterations = span_days // 7
            miss_chance = 0.25  # 25% chance to skip a week

        elif periodicity == "monthly":
            delta = timedelta(days=30)
            num_iterations = span_days // 30
            miss_chance = 0.33  # 33% chance to skip a month

        else:
            continue

        for i in range(num_iterations):
            ts = now - i * delta
            # Randomly skip some completions to simulate imperfect streaks
            if random() > miss_chance:
                manager.complete_habit(h.id, when=ts)


def add_perfect_streaks(manager: HabitManager, span_days: int = 60) -> None:
    """
    Add perfect streak completions for all habits (no misses).
    Useful for testing ideal analytics behavior.
    """

    habits = manager.list_habits()
    now = datetime.utcnow()

    for h in habits:
        periodicity = h.periodicity.lower()
        if periodicity == "daily":
            delta = timedelta(days=1)
            num_iterations = span_days
        elif periodicity == "weekly":
            delta = timedelta(weeks=1)
            num_iterations = span_days // 7
        elif periodicity == "monthly":
            delta = timedelta(days=30)
            num_iterations = span_days // 30
        else:
            continue

        for i in range(num_iterations):
            ts = now - i * delta
            manager.complete_habit(h.id, when=ts)


def show_admin_summary(manager: HabitManager) -> None:
    """
    Print debug summary of all habits and their completion counts.
    """
    habits = manager.list_habits()
    print(f"\n📋 {len(habits)} habits in DB:")
    for h in habits:
        print(f"  - {h.name:<20} [{h.periodicity}] ({len(h.completions)} completions)")

