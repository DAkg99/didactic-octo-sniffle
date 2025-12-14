import os
import datetime as dt
from dataclasses import dataclass
from typing import ClassVar

import movies
import seating
import storage
# import seating
# import bookings
# import storage
# import reports

# Done:
# Main: Schedule viewer
# Main: Movie details

# To-do:
# All unimplemented main features
# Schedule viewer pretty print
# Admin menu protection
# Admin booking cancellation

# Extra To-dos:
# Make schedule viewer send user directly to new booking, with data of requested showtime
# Colored terminal
# Clear terminal between prompts
# Prevent overlapping screenings (lol)

# Theater name
theater_name = "Testificate"
# Database path
data_path = "./data/"
# Backup path
backup_path = "./backup/"
# Create directories if absent
os.makedirs(backup_path, exist_ok=True)
os.makedirs(data_path, exist_ok=True)



@dataclass
class MenuSelector:
    """Each instance contains menu prompt & options. Method 'run' prints them and makes user choose (returns key)."""
    prompt_for_number: ClassVar[str] = "Enter a number: "
    number_selection_error: ClassVar[str] = "Invalid selection. Enter to continue."
    prompt: str
    options: list[dict[str, str]]

    @classmethod
    def dynamically_construct(cls, prompt: str, raw_options: list, add_back_option: bool = True):
        """Construct new instance using raw_options as options (keyed as string integers)."""
        options = []
        if add_back_option:
            options.append({"back": "[Go back]"})
        for index, option in enumerate(raw_options, bool(add_back_option)): # Start from 1 if [Go Back] was added.
            options.append({str(index): option})
        return cls(prompt,options)

    def run(self, prompt_override: str = "") -> str:
        """Displays menu until user makes a valid choice."""
        while True:
            self._print_menu(prompt_override)
            choice = self._make_user_choose()
            if not choice:
                input(MenuSelector.number_selection_error)
            break
        return choice

    def _print_menu(self, prompt_override: str):
        """Prints instance's prompt & options. Prompt can be overridden."""
        print((self.prompt * bool(not prompt_override)) +
              (str(prompt_override) * bool(prompt_override)))  # Branchless conditional
        for i, option in enumerate(self.options):
            print(f"{i}: {next(iter((option.values())))}")  # Make values iterable -> Iterate to next

    def _make_user_choose(self) -> str | None:
        """Prompts user to select an option & returns it. Returns None when invalid selection."""
        try:
            return next(iter(self.options[int(input(MenuSelector.prompt_for_number))].keys()))  # Return chosen key
        except (NameError, TypeError, IndexError):
            return None


# Initialise menu selection objects
main_selector = MenuSelector(
    "What would you like to do?", [                         # 1.Main
        {"admin": "[Staff Access]"},                        # 1.Submenu
        {"schedule": "View scheduled showtimes"},           # 2.Submenu
        {"book": "Book a ticket"},                          # 3.Submenu
        {"imdb": "Read more about available movies"}])      # 4.Submenu

schedule_selector = MenuSelector(
    "How would you like to view the schedule?", [           # 1.2 Schedule Viewing
        {"back": "[Go back]"},                              # BACK
        {"title": "Showtimes of a specific movie"},         # Action
        {"date": "All movies on a specific day"},           # Action
        {"all": "All movies"}])                             # Action

book_selector = MenuSelector(
    "Booking options:", [                                   # 1.3 Booking
        {"back": "[Go back]"},                              # BACK
        {"new_book": "Make a new booking"},                 # Action
        {"view_book": "View current bookings"},             # Action
        {"remove_book": "Cancel a booking"}])               # Action

admin_selector = MenuSelector(
    "What would you like to manage?", [                     # 1.1 Admin
        {"back": "[Exit Admin Mode]"},                      # BACK
        {"movies": "Manage movies & showtimes"},            # 1.Submenu
        {"reports": "Manage analytics"},                    # 2.Submenu
        {"backups": "Manage database backups"}])            # 3.Submenu

admin_movies_selector = MenuSelector(
    "Movie options:", [                                     # 1.1.1 Admin Movies
        {"back": "[Go back]"},                              # BACK
        {"new_movie": "Add a new movie"},                   # Action (TO DO) (Note: Ask to create new showing)
        {"rem_movie": "Retire a movie"},                    # Action (TO DO) (Note: Remove current showings)
        {"new_showing": "Add new showing to schedule"},     # Action (TO DO)
        {"rem_showing": "Remove a showing from schedule"}]) # Action (TO DO)

admin_reports_selector = MenuSelector(
    "Analytic options:", [                                  # 1.1.2 Admin Reports
        {"back": "[Go back]"},                              # BACK
        {"export": "Export all analytics to file"},         # Action (TO DO) (Note: reports.export_report())
        {"occupancy": "View occupancy statistics"},         # Action (TO DO) (Note: reports.occupancy_report())
        {"revenue": "View revenue summary"},                # Action (TO DO) (Note: reports.revenue_summary())
        {"top_movies": "View the most popular 5 movies"}])  # Action (TO DO) (Note: reports.top_movies())

admin_backups_selector = MenuSelector(
    "Backup options:", [                                    # 1.1.3 Admin Backups
        {"back": "[Go back]"},                              # BACK
        {"save_backup": "Create a manual backup of data"}]) # Action (TO DO) (Note: storage.backup_state())
        #{"": ""},                                            (TO DO: View, restore, delete backups)
        #{"": ""},
        #{"": ""}])

# Initialise menu selection objects which can't be hardcoded.
movie_view_selector = MenuSelector.dynamically_construct(          # 1.4 Movie Details
    "Select a movie to learn more about it:",                     # BACK & Actions
    cached_movies := [movie for movie in movies.load_movies(data_path)])


### Menus
def main_menu():
    while True:
        match main_selector.run():
            case "admin":
                admin_menu()
            case "schedule":
                schedule_menu()
            case "book":
                book_menu()
            case "imdb":
                movie_detail_menu()
            case _:
                raise NotImplemented

def schedule_menu():
    """Make user search through the schedule"""
    while True:
        match schedule_selector.run():
            case "back":
                return
            case "title":
                schedule_search_title()
            case "date":
                schedule_search_date()
            case "all":
                schedule_search_all()
            case _:
                raise NotImplemented

def book_menu():
    """Get user to view and manage bookings"""
    while True:
        match book_selector.run():
            case "back":
                return
            case "new_book":
                book_new()
            case "view_book":
                # Placeholder
                print("TO DO")
            case "remove_book":
                # Placeholder
                print("TO DO")
            case _:
                raise NotImplemented

def movie_detail_menu():
    while True:
        if (user_choice := movie_view_selector.run()) == "back":
            return
        user_movie = cached_movies[int(user_choice) - 1]
        movie_pretty_print(user_movie)

def admin_menu():
    """Admin main menu"""
    while True:
        match admin_selector.run():
            case "back":
                return
            case "movies":
                admin_movies_menu()
            case "reports":
                admin_reports_menu()
            case "backups":
                admin_backups_menu()
            case _:
                raise NotImplemented

def admin_movies_menu():
    """Admin menu to manage movies and showings"""
    while True:
        match admin_movies_selector.run():
            case "back":
                return
            case "new_movie":
                # movies.add_movie(...)
                print("[Placeholder]")
                input("Enter movie to add: ")
                input("Schedule viewings right away? (y/n) ")
                print("Movie has been added")
                pause_confirm()
            case "rem_movie":
                # movies.remove_movie(...)
                print("[Placeholder]")
                print("Scheduled viewings for this movie will also be removed")
                input("Enter movie to retire: ")
                print("Movie has been retired")
                pause_confirm()
            case "new_showing":
                # movies.schedule_showtime(...)
                print("[Placeholder]")
                movies.list_showtimes(data_path, None)
                input("Enter showtime to add: ")  # This will require a series of inputs
                print("New showtime has been added to schedule")
                pause_confirm()
            case "rem_showing":
                # movies.update_showtime
                print("[Placeholder]")
                movies.list_showtimes(data_path, None)
                input("Enter showtime to remove: ")  # This will require a series of inputs
                print("Showtime has been removed from schedule")
                pause_confirm()
            case _:
                raise NotImplemented

def admin_reports_menu():
    """Admin menu to view and export analytics"""
    while True:
        match admin_reports_selector.run():
            case "back":
                return
            case "export":
                # reports.export_report(...)
                print("[Placeholder]")
                print("Data exported to /path/file.json")
                pause_confirm()
            case "occupancy":
                # reports.occupancy_report(...)
                print("[Placeholder]")
                print("Theatre is 100% booked")
                pause_confirm()
            case "revenue":
                # reports.revenue_summary(...)
                print("[Placeholder]")
                print("Theatre has made 1 brouzouf")
                pause_confirm()
            case "top_movies":
                # reports.top_movies(...)
                print("[Placeholder]")
                print(f"Most popular movie is")
                pause_confirm()
            case _:
                raise NotImplemented

def admin_backups_menu():
    """Admin menu to export backups"""
    while True:
        match admin_backups_selector.run():
            case "back":
                return
            case "save_backup":
                # storage.backup_state(...)
                print("[Placeholder]")
                print("Backup saved to /path/file.json")
            case _:
                raise NotImplemented
        pause_confirm()


# General Helpers---------
def pause_confirm():
    input("[Enter to continue] ")
    
def print_list(my_list):
    [print(item) for item in my_list]
    pause_confirm()

# Schedule Search Functions---------
def schedule_search_title():
    if search_for := input(f"Enter movie title: "):
        print_list(movies.list_showtimes(data_path, search_for))

def schedule_search_date():
    if search_for := storage.user_input_verified_date():
        print_list(movies.list_showtimes(data_path, search_for))

def schedule_search_all():
    print_list(movies.list_showtimes(data_path))

# Book Functions---------
def book_new(): # Incomplete
    current_schedule = movies.list_showtimes(data_path)
    print("Current schedule: ")
    for index, item in enumerate(current_schedule,1):
        print(f"{index}:   {item["name"]}")
    seating.render_seat_map()

# Movie Details Functions---------
def movie_pretty_print(movie: movies.Movie):
    print(f"Title: {movie.title}\n"
          f"Genre: {', '.join(list(map(str,movie.genre))).capitalize()}\n"
          f"Duration: {str(movie.duration.seconds//3600)}H{str(movie.duration.seconds//60)+"M"}\n"
          f"Rating: {movie.rating:.2f}/5\n"
          f"Description: {movie.description}")
    pause_confirm()


# START
print(f"Welcome to {theater_name}!")
main_menu()