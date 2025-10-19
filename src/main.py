# src/main.py
from __future__ import annotations
import sys
from datetime import datetime
from typing import Optional

from modules.sqlite_handler import SQLiteHandler
from modules.habit_manager import HabitManager

# exact ASCII banner you provided
ASCII_BANNER = r"""
----------------------------------------------------------
 _   _       _     _ _ _____              _
| | | |     | |   (_) |_   _|            | |
| |_| | __ _| |__  _| |_| |_ __ __ _  ___| | _____ _ __
|  _  |/ _` | '_ \| | __| | '__/ _` |/ __| |/ / _ \ '__|
| | | | (_| | |_) | | |_| | | | (_| | (__|   <  __/ |
\_| |_/\__,_|_.__/|_|\__\_/_|  \__,_|\___|_|\_\___|_|

----------------------------------------------------------

Welcome to HabitTracker CLI!

Here's what you can do:
    🟢 Create a new habit
    🟡 Modify or delete an existing habit
    🔵 Mark a habit as completed
    🟣 Analyze your progress and streaks

You can see all available commands with the 'help' command.


What would you like to do? (type 'help' for options)
"""

USAGE_HELP = """
Here are all available commands you can run:

General navigation:
    q, quit, exit       -   exit the application
    l, list             -   list defined habits
    c, create           -   create a new habit
    b, banner           -   show the banner of the application
    d, delete           -   delete a habit by id
    e, edit             -   edit the values of a habit
    m, mark, complete   -   mark a habit as completed now
    h, help             -   show this help
"""

PROMPT = "HabitTracker > : "

VALID_PERIODICITIES = {"daily", "weekly", "monthly"}


def fmt_dt_for_list(dt: Optional[datetime]) -> str:
    """Format datetimes like: 'Oct 18, 2025 — 23:56' or '—' if None"""
    if dt is None:
        return "—"
    return dt.strftime("%b %d, %Y — %H:%M")


def print_banner_and_welcome() -> None:
    print(ASCII_BANNER)


def print_help() -> None:
    print(USAGE_HELP)


def print_habits_table(manager: HabitManager) -> None:
    habits = manager.list_habits()
    if not habits:
        print("\nNo habits found.\n")
        return

    # Sort descending by id (newest first) to match sample
    habits_sorted = sorted(habits, key=lambda h: (h.id or 0), reverse=True)

    print()
    print("ID    Name                 Periodicity     Created At")
    print("----------------------------------------------------------------------")
    for h in habits_sorted:
        created = fmt_dt_for_list(h.created_at)
        last = fmt_dt_for_list(max(h.completions) if h.completions else None)
        # Match column widths from your sample
        print(f"{h.id:<5} {h.name:<20} {h.periodicity:<15} {created}")
    print()


def cmd_create(manager: HabitManager) -> None:
    name = input("Enter habit name: ").strip()
    if not name:
        print("Aborted: name cannot be empty.")
        return
    periodicity = input("Enter periodicity (daily/weekly/monthly): ").strip().lower()
    if periodicity not in VALID_PERIODICITIES:
        print(f"Invalid periodicity '{periodicity}'. Must be one of: daily, weekly, monthly.")
        return
    try:
        habit = manager.create_habit(name=name, periodicity=periodicity)
    except Exception as exc:
        print(f"Error saving habit: {exc}")
        return
    print(f"\n✅ Habit '{habit.name}' ({habit.periodicity}) saved successfully!\n")


def cmd_list(manager: HabitManager) -> None:
    print_habits_table(manager)


def cmd_edit(manager: HabitManager) -> None:
    print_habits_table(manager)
    try:
        raw = input("Enter the ID of the habit you want to edit: ").strip()
        if not raw:
            print("Edit cancelled.")
            return
        hid = int(raw)
    except ValueError:
        print("Invalid ID.")
        return

    habit = manager.get_habit(hid)
    if habit is None:
        print(f"No habit with ID {hid}.")
        return

    new_name = input(f"Enter new habit name [{habit.name}]: ").strip()
    if new_name == "":
        new_name = habit.name

    new_period = input(f"Enter new periodicity (daily/weekly/monthly) [{habit.periodicity}]: ").strip().lower()
    if new_period == "":
        new_period = habit.periodicity
    if new_period not in VALID_PERIODICITIES:
        print(f"Invalid periodicity '{new_period}'. Update aborted.")
        return

    ok = manager.update_habit(hid, name=new_name, periodicity=new_period)
    if ok:
        print(f"\n✏️ Habit with ID {hid} updated successfully!\n")
    else:
        print("No changes were made.")


def cmd_delete(manager: HabitManager) -> None:
    print_habits_table(manager)
    try:
        raw = input("Enter the ID of the habit you want to delete: ").strip()
        if not raw:
            print("Delete cancelled.")
            return
        hid = int(raw)
    except ValueError:
        print("Invalid ID.")
        return

    confirm = input(f"Are you sure you want to delete habit ID {hid}? [y/N]: ").strip().lower()
    if confirm not in {"y", "yes"}:
        print("Delete cancelled.")
        return

    ok = manager.delete_habit(hid)
    if ok:
        print(f"\n🗑️ Habit with ID {hid} deleted successfully.\n")
    else:
        print(f"No habit with ID {hid} found.")


def cmd_complete(manager: HabitManager) -> None:
    print_habits_table(manager)
    try:
        raw = input("Enter the ID of the habit you want to mark completed: ").strip()
        if not raw:
            print("Complete cancelled.")
            return
        hid = int(raw)
    except ValueError:
        print("Invalid ID.")
        return

    ok = manager.complete_habit(hid)
    if ok:
        print(f"\n✅ Recorded completion for habit #{hid}.\n")
    else:
        print(f"Habit with id {hid} not found.")


def main_loop(db_path: str = "src/data/sample_habits.db") -> None:
    storage = SQLiteHandler(db_path)
    manager = HabitManager(storage)

    # Startup banner and welcome (exact text)
    print_banner_and_welcome()

    while True:
        try:
            raw = input(PROMPT)
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Exiting HabitTracker. Stay consistent and keep growing!")
            break

        cmd = raw.strip()
        if not cmd:
            continue

        low = cmd.lower()

        # exit commands
        if low in {"q", "quit", "exit"}:
            print("👋 Exiting HabitTracker. Stay consistent and keep growing!")
            break

        # help
        if low in {"help", "h", "?"}:
            print_help()
            continue

        # banner
        if low in {"b", "banner"}:
            print_banner_and_welcome()
            continue

        # list
        if low in {"l", "list"}:
            cmd_list(manager)
            continue

        # create
        if low in {"c", "create"}:
            cmd_create(manager)
            continue

        # edit
        if low in {"e", "edit"}:
            cmd_edit(manager)
            continue

        # delete
        if low in {"d", "delete"}:
            cmd_delete(manager)
            continue

        # complete / mark
        if low in {"m", "mark", "complete"}:
            cmd_complete(manager)
            continue

        # unknown
        print(f"Unknown command: {cmd!r}. Type 'help' to see available commands.")


if __name__ == "__main__":
    # Allow passing a custom DB path via CLI arg: `python main.py /path/to/db`
    if len(sys.argv) > 1:
        db_arg = sys.argv[1]
        main_loop(db_arg)
    else:
        main_loop()

