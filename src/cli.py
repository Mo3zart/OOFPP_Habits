import click

ASCII_ART = r"""
----------------------------------------------------------
 _   _       _     _ _ _____              _             
| | | |     | |   (_) |_   _|            | |            
| |_| | __ _| |__  _| |_| |_ __ __ _  ___| | _____ _ __ 
|  _  |/ _` | '_ \| | __| | '__/ _` |/ __| |/ / _ \ '__|
| | | | (_| | |_) | | |_| | | | (_| | (__|   <  __/ |   
\_| |_/\__,_|_.__/|_|\__\_/_|  \__,_|\___|_|\_\___|_|   
                                                        
----------------------------------------------------------
"""

STARTUP_TEXT = r"""
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
"""

def show_banner():
    click.clear()
    click.echo(click.style(ASCII_ART, fg='cyan'))
    click.secho(STARTUP_TEXT, fg='green')

def main_loop():
    while True:
        user_input = click.prompt(
            click.style("\nWhat would you like to do? (type 'help' for options)", fg='cyan')
        )

        if user_input in ['exit', 'quit', 'q']:
            click.secho("👋 Exiting HabitTracker. Stay consistent and keep growing!", fg='yellow')
            break
        if user_input == 'help':
            click.secho(HELP_MENU, fg='green')

def run():
    """Main entry point."""
    show_banner()
    main_loop()

if __name__ == '__main__':
    run()
