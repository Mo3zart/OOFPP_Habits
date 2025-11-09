""" main module for the Habit Tracker application.

Moritz Zewinger - OOFPP – DLBDSOOFPP01

This module is part of the student portfolio submission."""

# src/main.py
from __future__ import annotations
import sys
from datetime import datetime
from typing import Optional
from colorama import Fore, Style, init

from modules.sqlite_handler import SQLiteHandler
from modules.habit_manager import HabitManager
from modules import analytics, admin_tools

# initialize colorama
init(autoreset=True)

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
    q, quit, exit           -   exit the application
    l, list                 -   list defined habits
    c, create               -   create a new habit
    b, banner               -   show the banner of the application
    d, delete               -   delete a habit by id
    e, edit                 -   edit the values of a habit
    m, mark, complete       -   mark a habit as completed now
    h, help                 -   show this help
    a, analyze, analytics   -   analyze your habit performance
    streak <habit name>     -   show the longest streak for a specific habit

    admin                   - open admin panel (create dummy data, test streaks)


"""

PROMPT = Fore.YELLOW + "HabitTracker > : " + Style.RESET_ALL
VALID_PERIODICITIES = {"daily", "weekly", "monthly"}


def fmt_dt_for_list(dt: Optional[datetime]) -> str:
    """Format datetimes like: 'Oct 18, 2025 — 23:56' or '—' if None"""
    if dt is None:
        return "—"
    return dt.strftime("%b %d, %Y — %H:%M")


def print_banner_and_welcome() -> None:
    """Print banner and welcome.

    Moritz Zewinger - OOFPP – DLBDSOOFPP01

    Args:
        None

    Returns:
        None
    """

    print(Fore.CYAN + ASCII_BANNER + Style.RESET_ALL)


def print_help() -> None:
    """Print help.

    Moritz Zewinger - OOFPP – DLBDSOOFPP01

    Args:
        None

    Returns:
        None
    """

    print(Fore.CYAN + USAGE_HELP + Style.RESET_ALL)


def print_habits_table(manager: HabitManager) -> None:
    """Print habits table.

    Moritz Zewinger - OOFPP – DLBDSOOFPP01

    Args:
        manager: Description.

    Returns:
        None
    """

    habits = manager.list_habits()
    if not habits:
        print(Fore.RED + "\nNo habits found.\n" + Style.RESET_ALL)
        return

    habits_sorted = sorted(habits, key=lambda h: (h.id or 0), reverse=True)

    print(Fore.CYAN + "\nID    Name                 Periodicity     Created At               Last Completion")
    print("---------------------------------------------------------------------------------------------")
    for h in habits_sorted:
        created = fmt_dt_for_list(h.created_at)
        last = fmt_dt_for_list(max(h.completions) if h.completions else None)
        print(f"{h.id:<5} {h.name:<20} {h.periodicity:<15} {created:<25} {last}")
    print(Style.RESET_ALL)


def cmd_create(manager: HabitManager) -> None:
    """Cmd create.

    Moritz Zewinger - OOFPP – DLBDSOOFPP01

    Args:
        manager: Description.

    Returns:
        None
    """

    name = input(Fore.YELLOW + "Enter habit name: " + Style.RESET_ALL).strip()
    if not name:
        print(Fore.RED + "Aborted: name cannot be empty." + Style.RESET_ALL)
        return
    periodicity = input(Fore.YELLOW + "Enter periodicity (daily/weekly/monthly): " + Style.RESET_ALL).strip().lower()
    if periodicity not in VALID_PERIODICITIES:
        print(Fore.RED + f"Invalid periodicity '{periodicity}'. Must be one of: daily, weekly, monthly." + Style.RESET_ALL)
        return
    try:
        habit = manager.create_habit(name=name, periodicity=periodicity)
    except Exception as exc:
        print(Fore.RED + f"Error saving habit: {exc}" + Style.RESET_ALL)
        return
    print(Fore.GREEN + f"\n✅ Habit '{habit.name}' ({habit.periodicity}) saved successfully!\n" + Style.RESET_ALL)


def cmd_list(manager: HabitManager) -> None:
    """Cmd list.

    Moritz Zewinger - OOFPP – DLBDSOOFPP01

    Args:
        manager: Description.

    Returns:
        None
    """

    print_habits_table(manager)


def cmd_edit(manager: HabitManager) -> None:
    """Cmd edit.

    Moritz Zewinger - OOFPP – DLBDSOOFPP01

    Args:
        manager: Description.

    Returns:
        None
    """

    print_habits_table(manager)
    try:
        raw = input(Fore.YELLOW + "Enter the ID of the habit you want to edit: " + Style.RESET_ALL).strip()
        if not raw:
            print(Fore.RED + "Edit cancelled." + Style.RESET_ALL)
            return
        hid = int(raw)
    except ValueError:
        print(Fore.RED + "Invalid ID." + Style.RESET_ALL)
        return

    habit = manager.get_habit(hid)
    if habit is None:
        print(Fore.RED + f"No habit with ID {hid}." + Style.RESET_ALL)
        return

    new_name = input(Fore.YELLOW + f"Enter new habit name [{habit.name}]: " + Style.RESET_ALL).strip()
    if new_name == "":
        new_name = habit.name

    new_period = input(Fore.YELLOW + f"Enter new periodicity (daily/weekly/monthly) [{habit.periodicity}]: " + Style.RESET_ALL).strip().lower()
    if new_period == "":
        new_period = habit.periodicity
    if new_period not in VALID_PERIODICITIES:
        print(Fore.RED + f"Invalid periodicity '{new_period}'. Update aborted." + Style.RESET_ALL)
        return

    ok = manager.update_habit(hid, name=new_name, periodicity=new_period)
    if ok:
        print(Fore.GREEN + f"\n✏️ Habit with ID {hid} updated successfully!\n" + Style.RESET_ALL)
    else:
        print(Fore.RED + "No changes were made." + Style.RESET_ALL)


def cmd_delete(manager: HabitManager) -> None:
    """Cmd delete.

    Moritz Zewinger - OOFPP – DLBDSOOFPP01

    Args:
        manager: Description.

    Returns:
        None
    """

    print_habits_table(manager)
    try:
        raw = input(Fore.YELLOW + "Enter the ID of the habit you want to delete: " + Style.RESET_ALL).strip()
        if not raw:
            print(Fore.RED + "Delete cancelled." + Style.RESET_ALL)
            return
        hid = int(raw)
    except ValueError:
        print(Fore.RED + "Invalid ID." + Style.RESET_ALL)
        return

    confirm = input(Fore.YELLOW + f"Are you sure you want to delete habit ID {hid}? [y/N]: " + Style.RESET_ALL).strip().lower()
    if confirm not in {"y", "yes"}:
        print(Fore.CYAN + "Delete cancelled." + Style.RESET_ALL)
        return

    ok = manager.delete_habit(hid)
    if ok:
        print(Fore.GREEN + f"\n🗑️ Habit with ID {hid} deleted successfully.\n" + Style.RESET_ALL)
    else:
        print(Fore.RED + f"No habit with ID {hid} found." + Style.RESET_ALL)


def cmd_complete(manager: HabitManager) -> None:
    """Cmd complete.

    Moritz Zewinger - OOFPP – DLBDSOOFPP01

    Args:
        manager: Description.

    Returns:
        None
    """

    print_habits_table(manager)
    try:
        raw = input(Fore.YELLOW + "Enter the ID of the habit you want to mark completed: " + Style.RESET_ALL).strip()
        if not raw:
            print(Fore.RED + "Complete cancelled." + Style.RESET_ALL)
            return
        hid = int(raw)
    except ValueError:
        print(Fore.RED + "Invalid ID." + Style.RESET_ALL)
        return

    ok = manager.complete_habit(hid)
    if ok:
        print(Fore.GREEN + f"\n✅ Recorded completion for habit #{hid}.\n" + Style.RESET_ALL)
    else:
        print(Fore.RED + f"Habit with id {hid} not found." + Style.RESET_ALL)


def main_loop(db_path: str = "src/data/sample_habits.db") -> None:
    """Main loop.

    Moritz Zewinger - OOFPP – DLBDSOOFPP01

    Args:
        db_path: Description.

    Returns:
        None
    """

    storage = SQLiteHandler(db_path)
    manager = HabitManager(storage)
    print_banner_and_welcome()

    while True:
        try:
            raw = input(PROMPT)
        except (KeyboardInterrupt, EOFError):
            print(Fore.CYAN + "\n👋 Exiting HabitTracker. Stay consistent and keep growing!" + Style.RESET_ALL)
            break

        cmd = raw.strip()
        if not cmd:
            continue
        low = cmd.lower()

        if low in {"q", "quit", "exit"}:
            print(Fore.CYAN + "👋 Exiting HabitTracker. Stay consistent and keep growing!" + Style.RESET_ALL)
            break
        elif low in {"help", "h", "?"}:
            print_help()
        elif low in {"b", "banner"}:
            print_banner_and_welcome()
        elif low in {"l", "list"}:
            cmd_list(manager)
        elif low in {"c", "create"}:
            cmd_create(manager)
        elif low in {"e", "edit"}:
            cmd_edit(manager)
        elif low in {"d", "delete"}:
            cmd_delete(manager)
        elif low in {"m", "mark", "complete"}:
            cmd_complete(manager)
        elif low in {"a", "analyze", "analytics"}:
            print(Fore.CYAN + "\n=== Habit Analytics ===\n" + Style.RESET_ALL)
            habits = manager.list_habits()
            if not habits:
                print(Fore.RED + "No habits found for analysis." + Style.RESET_ALL)
                continue
            longest = analytics.longest_streak_overall(habits)
            print(Fore.GREEN + f"🏆 Longest streak overall: {longest[0]} — {longest[1]} completions" + Style.RESET_ALL)
            print(Fore.YELLOW + "\n🔹 Daily Habits:" + Style.RESET_ALL)
            daily = analytics.list_by_periodicity(habits, "daily")
            if daily:
                for h in daily:
                    print(f"  {Fore.WHITE}{h.name}{Style.RESET_ALL}")
            else:
                print(Fore.RED + "  None" + Style.RESET_ALL)
            print(Fore.BLUE + "\n🔹 Weekly Habits:" + Style.RESET_ALL)
            weekly = analytics.list_by_periodicity(habits, "weekly")
            if weekly:
                for h in weekly:
                    print(f"  {Fore.WHITE}{h.name}{Style.RESET_ALL}")
            else:
                print(Fore.RED + "  None" + Style.RESET_ALL)
            print(Fore.MAGENTA + "\n🔹 Monthly Habits:" + Style.RESET_ALL)
            monthly = analytics.list_by_periodicity(habits, "monthly")
            if monthly:
                for h in monthly:
                    print(f"  {Fore.WHITE}{h.name}{Style.RESET_ALL}")
            else:
                print(Fore.RED + "  None" + Style.RESET_ALL)
            print(Fore.CYAN + "\n📈 Individual Streaks:" + Style.RESET_ALL)
            for h in habits:
                streak = analytics.calculate_streaks(h)
                color = Fore.GREEN if streak >= 10 else Fore.YELLOW if streak >= 5 else Fore.RED
                print(f"  {h.name:<15} — {color}{streak}{Style.RESET_ALL}")

        elif low in {"admin"}:
            print(Fore.CYAN + "\n=== HabitTracker Admin Console ===" + Style.RESET_ALL)
            print("Type 'help' to see available options, or 'back' to return to main menu.\n")

            def show_admin_help():
                """Show admin help.

                Moritz Zewinger - OOFPP – DLBDSOOFPP01

                Args:
                    None

                Returns:
                    None
                """

                print(Fore.CYAN + "\nAdmin Commands:\n" + Style.RESET_ALL)
                print("  show <habit_id>     - show detailed info for a specific habit")
                print("  completions         - list all recorded completions")
                print("  back, exit, q       - return to main menu\n")

            show_admin_help()

            while True:
                choice = input(Fore.YELLOW + "Admin > " + Style.RESET_ALL).strip().lower()

                if choice in {"back", "exit", "b", "q", "quit"}:
                    print(Fore.CYAN + "Returning to main menu..." + Style.RESET_ALL)
                    break

                elif choice in {"help", "h"}:
                    show_admin_help()

                elif choice.startswith("show "):
                    parts = choice.split()
                    if len(parts) != 2 or not parts[1].isdigit():
                        print(Fore.RED + "Usage: show <habit_id>" + Style.RESET_ALL)
                        continue
                    habit_id = int(parts[1])
                    admin_tools.show_habit_details(manager, habit_id)

                elif choice in {"completions", "list completions"}:
                    admin_tools.show_all_completions(manager)

                else:
                    print(Fore.RED + f"❌ Unknown command: '{choice}'. Type 'help' for options." + Style.RESET_ALL)

        elif low.startswith("streak "):
            _, *rest = low.split()
            name = " ".join(rest)
            if not name:
                print(Fore.RED + "Usage: streak <habit name>" + Style.RESET_ALL)
                continue
            habits = manager.list_habits()
            streak = analytics.longest_streak_for_habit_name(habits, name)
            if streak is None:
                print(Fore.RED + f"Habit '{name}' not found." + Style.RESET_ALL)
            else:
                print(Fore.GREEN + f"🔥 Longest streak for '{name}': {streak}" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"Unknown command: {cmd!r}. Type 'help' to see available commands." + Style.RESET_ALL)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main_loop(sys.argv[1])
    else:
        main_loop()
