import click
from datetime import datetime
from .habit import Habit
from .sqlite_handler import SQLiteHandler

class HabitManager:
    def __init__(self, db_path=None):
        self.db = SQLiteHandler(db_path)

    def create_habit(self, name, periodicity):
        """Create a new habit and save it to the database."""
        habit = Habit(name, periodicity)
        self.db.save(habit)
        return f"\n✅ Habit '{habit.name}' ({habit.periodicity}) saved successfully!"

    def list_habits(self):
        habits = self.db.load()
        if not habits:
            return click.style("📭 No habits found.", fg='yellow')
        header = click.style(f"\n{'ID':<5} {'Name':<20} {'Periodicity':<15} {'Created At':<25}",
                             fg='cyan',
                             bold=True)
        separator = click.style("-" * 70, fg='cyan')
        rows = []
        for h in habits:
            try:
                created = datetime.fromisoformat(h[3]).strftime("%b %d, %Y — %H:%M")
            except Exception:
                created = h[3]
            row = f"{h[0]:<5} {h[1]:<20} {h[2]:<15} {created:<25}"
            rows.append(click.style(row, fg='magenta'))
        return f"{header}\n{separator}\n" + "\n".join(rows)

    def edit_habit(self, habit_id, new_name=None, new_periodicity=None):
        """Edit a habit's name or periodicity."""
        success = self.db.update(habit_id, new_name, new_periodicity)
        if success:
            return click.style(f"\n✏️ Habit with ID {habit_id} updated successfully!",
                               fg='green')
        else:
            return click.style(f"\n⚠️ No habit found with ID {habit_id}, or no changes made.",
                               fg='red')


    def delete_habit(self, habit_id):
        """Delete the habit by its ID."""
        success = self.db.delete(habit_id)
        if success:
            return click.style(f"\n🗑️ Habit with ID {habit_id} deleted successfully.",
                               fg='green')
        else:
            return click.style(f"\n⚠️ No habit found with ID {habit_id}.",
                               fg='red')
