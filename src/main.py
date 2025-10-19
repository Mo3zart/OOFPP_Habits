from __future__ import annotations
import sys
from typing import Optional

import click
from modules.sqlite_handler import SQLiteHandler
from modules.habit_manager import HabitManager

DEFAULT_DB = "src/data/sample_habits.db"

ASCII_BANNER = r"""
 _   _       _ _     _            _             _             
| | | | __ _| (_)___| |_ __ _ ___| |_ __ _ _ __| |_ ___  _ __ 
| |_| |/ _` | | / __| __/ _` / __| __/ _` | '__| __/ _ \| '__|
|  _  | (_| | | \__ \ || (_| \__ \ || (_| | |  | || (_) | |   
|_| |_|\__,_|_|_|___/\__\__,_|___/\__\__,_|_|   \__\___/|_|   

Welcome to the Habit Tracker CLI Framework
Type 'help' to see available commands or 'exit' to quit.
----------------------------------------------------------------
"""

# ---------------------------------------------------------------------
# Click CLI definition (for non-interactive use or internal dispatch)
# ---------------------------------------------------------------------
@click.group()
@click.option("--db", "-d", default=DEFAULT_DB, help="Path to SQLite database file.")
@click.pass_context
def cli(ctx: click.Context, db: str) -> None:
    """Habit Tracker CLI."""
    storage = SQLiteHandler(db)
    manager = HabitManager(storage)
    ctx.obj = {"storage": storage, "manager": manager}


@cli.command("add")
@click.argument("name")
@click.argument("periodicity")
@click.pass_context
def add_habit(ctx: click.Context, name: str, periodicity: str) -> None:
    """Add a new habit."""
    manager: HabitManager = ctx.obj["manager"]
    habit = manager.create_habit(name=name, periodicity=periodicity)
    click.echo(f"Created habit #{habit.id}: {habit.name} ({habit.periodicity})")


@cli.command("list")
@click.option("--periodicity", "-p", default=None, help="Filter by periodicity.")
@click.pass_context
def list_habits(ctx: click.Context, periodicity: Optional[str]) -> None:
    """List all habits."""
    manager: HabitManager = ctx.obj["manager"]
    habits = manager.list_habits()
    if periodicity:
        habits = [h for h in habits if h.periodicity == periodicity]
    if not habits:
        click.echo("No habits found.")
        return
    click.echo("\nID | Name                      | Periodicity | Created At               | Last Completion")
    click.echo("-" * 85)
    for h in habits:
        latest = max(h.completions).isoformat() if h.completions else "—"
        click.echo(f"{h.id:>2} | {h.name:<25} | {h.periodicity:<11} | {h.created_at:%Y-%m-%d %H:%M:%S} | {latest}")


@cli.command("complete")
@click.argument("habit_id", type=int)
@click.pass_context
def complete(ctx: click.Context, habit_id: int) -> None:
    """Mark a habit as completed now."""
    manager: HabitManager = ctx.obj["manager"]
    ok = manager.complete_habit(habit_id)
    click.echo("Completion recorded." if ok else f"Habit #{habit_id} not found.")


@cli.command("show")
@click.argument("habit_id", type=int)
@click.pass_context
def show(ctx: click.Context, habit_id: int) -> None:
    """Show one habit's details and completions."""
    manager: HabitManager = ctx.obj["manager"]
    habit = manager.get_habit(habit_id)
    if habit is None:
        click.echo(f"Habit #{habit_id} not found.")
        return
    click.echo(f"\n#{habit.id} {habit.name} ({habit.periodicity})  Created: {habit.created_at:%Y-%m-%d %H:%M}")
    if not habit.completions:
        click.echo("No completions yet.")
        return
    click.echo("Completions:")
    for c in habit.completions:
        click.echo(f" - {c:%Y-%m-%d %H:%M}")


@cli.command("edit")
@click.argument("habit_id", type=int)
@click.option("--name", default=None, help="New name.")
@click.option("--periodicity", default=None, help="New periodicity.")
@click.pass_context
def edit(ctx: click.Context, habit_id: int, name: Optional[str], periodicity: Optional[str]) -> None:
    """Edit an existing habit."""
    manager: HabitManager = ctx.obj["manager"]
    ok = manager.update_habit(habit_id, name=name, periodicity=periodicity)
    click.echo("Habit updated." if ok else "No habit updated.")


@cli.command("delete")
@click.argument("habit_id", type=int)
@click.pass_context
def delete(ctx: click.Context, habit_id: int) -> None:
    """Delete a habit."""
    manager: HabitManager = ctx.obj["manager"]
    ok = manager.delete_habit(habit_id)
    click.echo("Habit deleted." if ok else f"Habit #{habit_id} not found.")


# ---------------------------------------------------------------------
# Interactive shell implementation
# ---------------------------------------------------------------------
def interactive_shell(db_path: str = DEFAULT_DB) -> None:
    """Run an interactive CLI loop."""
    print(ASCII_BANNER)
    storage = SQLiteHandler(db_path)
    manager = HabitManager(storage)
    ctx = click.Context(cli, obj={"storage": storage, "manager": manager})

    while True:
        try:
            raw = input("habit-tracker > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting Habit Tracker. Goodbye!")
            break

        if not raw:
            continue
        if raw.lower() in {"exit", "quit"}:
            print("Exiting Habit Tracker. Goodbye!")
            break
        if raw.lower() in {"help", "?"}:
            cli.main(args=["--help"], prog_name="habit-tracker", standalone_mode=False)
            continue

        # Split command string and execute through Click
        argv = raw.split()
        try:
            cli.main(args=argv, prog_name="habit-tracker", standalone_mode=False, parent=ctx)
        except SystemExit:
            # Click may raise SystemExit on aborts; ignore to stay in loop
            continue
        except Exception as e:
            click.echo(f"[Error] {e}", err=True)


# ---------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # If user passed arguments, run as normal CLI once; otherwise, open shell
    if len(sys.argv) > 1:
        cli()
    else:
        interactive_shell()

