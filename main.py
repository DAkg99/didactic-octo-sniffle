import os
from dataclasses import dataclass, field
from typing import ClassVar

import movies
import seating
import bookings

# import storage
# import reports

# To-do:
# All the stuff that isn't done yet (shown through comments throughout. also check pdf for overview, outcomes, func. reqs.)
# Hide (?) and/or password-protect the admin menu.
# Admins should be able to cancel bookings, i guess
# Don't forget to ask for full name and email during booking. Important for viewing current bookings & refunds.
# Probably ask for age and other stuff to implement discounts.
# Prettier print for viewing schedule. Also don't print past viewings.
# Date verification (valid format? in the future?) wherever applicable e.g. when user views schedule by inputting date.
# ^ Time verification too
# Movie name verification wherever applicable e.g. when user views schedule by inputting name.
# Import sys to clear the terminal between menu navigation
# Import datetime to get current date for date verification and viewing print.
# Add duration/hall verification to prevent overlapping screenings (probably dont actually implement this)


# Database path
data_path = "./data/"
# Backup path
backup_path = "./backup/"
# Create directories if absent
os.makedirs(backup_path, exist_ok=True)
os.makedirs(data_path, exist_ok=True)


@dataclass
class Menu:
    prompt_for_number: ClassVar[str] = "Enter a number: "
    number_selection_error: ClassVar[str] = "Invalid selection. Enter to continue."
    prompt: str
    options: list[dict[str, str]]

    def select(self, prompt_override=""):
        """Displays menu until user makes a valid choice."""
        while True:
            self._print_menu(prompt_override)
            choice = self._make_user_choose()
            if choice == -1:
                input(Menu.number_selection_error)
                continue
            return choice

    def _print_menu(self, prompt_override):
        """Prints instance's prompt & options. Prompt can be overridden."""
        print((self.prompt * bool(not prompt_override)) +
              (str(prompt_override) * bool(prompt_override)))  # Branchless conditional
        for i, option in enumerate(self.options):
            print(f"{i}: {next(iter((option.values())))}")  # Make values iterable -> Iterate to next

    def _make_user_choose(self):
        """Prompts user to select an option & returns it. Returns -1 if invalid selection."""
        try:
            return next(iter(self.options[int(input(Menu.prompt_for_number))].keys()))  # Return chosen key
        except (NameError, TypeError, IndexError):
            return -1


# Initialise all menus
main_menu = Menu(
    "What would you like to do?", [
        {"admin": "[Staff Access]"},
        {"schedule": "View scheduled showtimes"},  # Submenu
        {"book": "Book a ticket"},
        {"see_bookings": "View current bookings"},
        {"unbook": "Cancel booking"}])

schedule_menu = Menu(
    "How would you like to view the schedule?", [
        {"back": "[Go back]"},
        {"name": "Showtimes of a specific movie"},
        {"date": "All movies on a specific day"},
        {"all": "All movies"}])

admin_menu = Menu(
    "What would you like to manage?", [
        {"back": "[Exit Admin Mode]"},
        {"movies": "Manage movies & showtimes"},  # Submenu
        {"reports": "Manage analytics"},  # Submenu
        {"backups": "Manage database backups"}])  # Submenu

admin_movies_menu = Menu(
    "Movie options:", [
        {"back": "[Go back]"},
        {"new_movie": "Add a new movie"},  # Add to movie list. Ask if new schedule should be made.
        {"rem_movie": "Retire a movie"},  # Remove from movie list. Should also remove it from schedule.
        {"new_showing": "Add new showing to schedule"},
        {"rem_showing": "Remove a showing from schedule"}])

admin_reports_menu = Menu(
    "Analytic options:", [
        {"back": "[Go back]"},
        {"export": "Export all analytics to file"},  # reports.export_report()
        {"occupancy": "View occupancy statistics"},  # reports.occupancy_report()
        {"revenue": "View revenue summary"},  # reports.revenue_summary()
        {"top_movies": "View the most popular 5 movies"}])  # reports.top_movies()

admin_backups_menu = Menu(
    "Backup options:", [
        {"back": "[Go back]"},
        {"save_backup": "Create a manual backup of data"}])  # storage.backup_state()


# "2": "": ""},
# "3": "": ""},
# "4": "": ""}


### Menus
def schedule_menu():
    """Menu to view and search the showtime schedule"""
    while True:
        menu_action = main_menu.select()
        match menu_action:
            case "back":
                return
            case "all":
                [print(showing) for showing in movies.list_showtimes(data_path, menu_action)]
                input("\n[Enter to continue] ")
            case "date" | "name":
                print("Date format: YYYY-MM-DD\n" * (menu_action == "date"), end="")
                search_for = input(f"Enter {menu_action}: ")
                [print(showing) for showing in movies.list_showtimes(data_path, menu_action, search_for)]
                input("\n[Enter to continue] ")
            case _:
                print("Not a recognised action.")


def admin_menu():
    """Admin main menu (directory of sub-menus)"""
    while True:
        menu_action = show_menu(admin_main_data)
        match menu_action:
            case "back":
                return
            case "movies":
                admin_movies_menu()
            case "reports":
                admin_reports_menu()
            case "backups":
                admin_backups_menu()
            case _:
                print("Invalid selection.")


def admin_movies_menu():
    """Admin menu to manage movies and showings"""
    while True:
        menu_action = show_menu(admin_movies_data)
        match menu_action:
            case "back":
                return
            case "new_movie":
                # movies.add_movie(...)
                print("[Placeholder]")
                input("Enter movie to add: ")
                input("Schedule viewings right away? (y/n) ")
                print("Movie has been added")
                input("[Enter to continue] ")
            case "rem_movie":
                # movies.removie_movie(...)
                print("[Placeholder]")
                print("Scheduled viewings for this movie will also be removed")
                input("Enter movie to retire: ")
                print("Movie has been retired")
                input("[Enter to continue] ")
            case "new_showing":
                # movies.schedule_showtime(...)
                print("[Placeholder]")
                movies.list_showtimes(data_path, "all", None)
                input("Enter showtime to add: ")  # This will require a series of inputs
                print("New showtime has been added to schedule")
                input("[Enter to continue] ")
            case "rem_showing":
                # movies.update_showtime
                print("[Placeholder]")
                movies.list_showtimes(data_path, "all", None)
                input("Enter showtime to remove: ")  # This will require a series of inputs
                print("Showtime has been removed from schedule")
                input("[Enter to continue] ")
            case _:
                print("Not a recognised action.")


def admin_reports_menu():
    """Admin menu to view and export analytics"""
    while True:
        menu_action = show_menu(admin_reports_data)
        match menu_action:
            case "back":
                return
            case "export":
                # reports.export_report(...)
                print("[Placeholder]")
                print("Data exported to /path/file.json")
                input("[Enter to continue] ")
            case "occupancy":
                # reports.occupancy_report(...)
                print("[Placeholder]")
                print("Theatre is 100% booked")
                input("[Enter to continue] ")
            case "revenue":
                # reports.revenue_summary(...)
                print("[Placeholder]")
                print("Theatre has made 1 brouzouf")
                input("[Enter to continue] ")
            case "top_movies":
                # reports.top_movies(...)
                print("[Placeholder]")
                print(f"Most popular movie is {movies.load_movies(data_path)[0]}")
                input("[Enter to continue] ")
            case _:
                print("Not a recognised action.")


def admin_backups_menu():
    """Admin menu to export backups"""
    while True:
        menu_action = show_menu(admin_backups_data)
        match menu_action:
            case "back":
                return
            case "save_backup":
                # storage.backup_state(...)
                print("[Placeholder]")
                print("Backup saved to /path/file.json")
            case _:
                print("Not a recognised action.")
        input("[Enter to continue] ")


# Main menu
while True:
    user_action = show_menu(main_menu_data)
    match user_action:
        case "schedule":
            schedule_menu()
        case "book":
            # bookings.create_booking()
            input("To do")
        case "see_bookings":
            # list_customer_bookings()
            input("To do")
        case "unbook":
            # bookings.cancel_booking()
            input("To do")
        case "admin":
            admin_menu()
        case _:
            print("Not a recognised action.")