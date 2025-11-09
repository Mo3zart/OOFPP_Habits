""" admin_tools module for the Habit Tracker application.

Moritz Zewinger - OOFPP – DLBDSOOFPP01

This module is part of the student portfolio submission."""

# src/modules/admin_tools.py
from __future__ import annotations
from datetime import datetime 
from .habit_manager import HabitManager
from . import analytics

from colorama import Fore, Style


def show_habit_details(manager: HabitManager, habit_id: int) -> None:
    """
    Show detailed information for a specific habit.
    Includes creation date, periodicity, total completions, longest streak, and last completion.
    """
    habit = manager.get_habit(habit_id)
    if not habit:
        print(Fore.RED + f"No habit found with ID {habit_id}." + Style.RESET_ALL)
        return

    total_completions = len(habit.completions)
    last_completion = max(habit.completions) if habit.completions else None
    last_str = last_completion.strftime("%b %d, %Y — %H:%M") if last_completion else "—"
    streak = manager.get_streak(habit.name)

    print(Fore.CYAN + f"""
Habit #{habit.id} — "{habit.name}"
  Periodicity: {habit.periodicity}
  Created at: {habit.created_at.strftime("%b %d, %Y — %H:%M")}
  Total completions: {total_completions}
  Longest streak: {streak}
  Last completed: {last_str}
""" + Style.RESET_ALL)


def show_habit_details(manager, habit_id: int) -> None:
    """Display detailed information for a single habit."""
    habit = manager.get_habit(habit_id)
    if not habit:
        print(Fore.RED + f"❌ No habit found with ID {habit_id}." + Style.RESET_ALL)
        return

    streak = analytics.calculate_streaks(habit)

    print(Fore.CYAN + f"\n📘 Habit Details (ID: {habit.id})" + Style.RESET_ALL)
    print(f"Name: {habit.name}")
    print(f"Periodicity: {habit.periodicity}")
    print(f"Created At: {habit.created_at.strftime('%b %d, %Y — %H:%M')}")
    print(f"Total Completions: {len(habit.completions)}")
    print(f"🔥 Current Streak: {streak}")

    if habit.completions:
        print(Fore.CYAN + "\nRecent Completions:" + Style.RESET_ALL)
        for c in reversed(habit.completions[-5:]):
            print(f"  • {c.strftime('%b %d, %Y — %H:%M')}\n")
    else:
        print(Fore.RED + "\nNo completions recorded yet.\n" + Style.RESET_ALL)


def show_all_completions(manager: HabitManager) -> None:
    """
    Display all recorded completions (habit_id, name, timestamp).
    """
    completions = manager.storage.get_all_completions()
    if not completions:
        print(Fore.RED + "No completions found." + Style.RESET_ALL)
        return

    print(Fore.CYAN + "\nAll Recorded Completions:" + Style.RESET_ALL)
    print(Fore.BLUE + "Habit ID    Habit Name           Timestamp" + Style.RESET_ALL)
    print(Fore.BLUE + "---------------------------------------------" + Style.RESET_ALL)

    for habit_id, habit_name, ts in completions:
        try:
            dt = datetime.fromisoformat(ts)
            ts_fmt = dt.strftime("%b %d, %Y — %H:%M")
        except Exception:
            ts_fmt = ts
        print(f"{habit_id:<10} {habit_name:<20} {ts_fmt}")

    print()
