import click
import modules.habit_manager as habit_manager
import modules.sqlite_handler as sqlite_handler

ASCII_ART = r"""
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
"""

HELP_MENU = r"""
Here are all available commands you can run:

General navigation:
    q, quit, exit       -   exit the application
    l, list             -   list defined habits
    c, create           -   creat a new habit
    b, banner           -   show the banner of the application
    d, delete           -   delete a habit by id
    e, edit             -   edit the values of a habit
"""

def show_banner():
    click.clear()
    click.echo(click.style(ASCII_ART, fg='cyan'))
    click.echo(click.style("\nWhat would you like to do? (type 'help' for options)", fg='cyan'))

def main_loop():
    manager = habit_manager.HabitManager()
    while True:
        user_input = click.prompt(
            click.style("\nHabitTracker > ", fg='cyan')
        )
        if user_input in ['exit', 'quit', 'q']:
            click.secho("👋 Exiting HabitTracker. Stay consistent and keep growing!", fg='yellow')
            break
        if user_input == 'help':
            click.secho(HELP_MENU, fg='green')
        if user_input in ['l', 'list']:
            habits = manager.list_habits()
            click.secho(habits, fg='magenta')
        if user_input in ['c', 'create']:
            name = click.prompt(click.style("Enter habit name", fg='yellow'))
            periodicity = click.prompt(click.style("Enter periodicity (daily/weekly/monthly)", fg='yellow'))
            result = manager.create_habit(name, periodicity)
            click.secho(result, fg='green')
        if user_input in ['b', 'banner']:
            show_banner()
        if user_input in ['d', 'delete']:
            click.secho(manager.list_habits(), fg='magenta')
            habit_id = click.prompt(click.style("Enter the ID of the habit you want to delete", fg='yellow'))
            try:
                habit_id = int(habit_id)
                confirm = click.confirm(
                    click.style(f"Are you sure you want to delete habit ID {habit_id}?", fg='yellow'),
                    default=False
                )

                if confirm:
                    result = manager.delete_habit(habit_id)
                    click.secho(result)
                else:
                    click.secho("❎ Deletion cancelled.", fg='cyan')

            except ValueError:
                click.secho("\n❌ Please enter a valid numeric ID.", fg='red')
        
        if user_input in ['e', 'edit']:
            click.secho(manager.list_habits(), fg='magenta')
            habit_id = click.prompt(click.style("\nEnter the ID of the habit you want to edit", fg='yellow'))

            try:
                habit_id = int(habit_id)
                habit = manager.db.get_by_id(habit_id)

                if not habit:
                    click.secho(f"\n⚠️ No habit found with ID {habit_id}.", fg='red')
                    continue

                current_name = habit[1]
                current_periodicity = habit[2]

                # Ask for new values with current ones as defaults
                new_name = click.prompt(
                    click.style(f"\nEnter new habit name [{current_name}]", fg='yellow'),
                    default=current_name,
                    show_default=False
                )

                new_periodicity = click.prompt(
                    click.style(f"Enter new periodicity (daily/weekly/monthly) [{current_periodicity}]", fg='yellow'),
                    default=current_periodicity,
                    show_default=False
                )

                # Only update if something actually changed
                if new_name == current_name and new_periodicity == current_periodicity:
                    click.secho("\n⚠️ No changes made.", fg='cyan')
                else:
                    result = manager.edit_habit(habit_id, new_name, new_periodicity)
                    click.secho(result)

            except ValueError:
                click.secho("\n❌ Please enter a valid numeric ID.", fg='red')
         

def run():
    """Main entry point."""
    show_banner()
    main_loop()

if __name__ == '__main__':
    run()
