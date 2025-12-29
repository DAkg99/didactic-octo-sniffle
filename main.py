import os
import getpass
import datetime as dt
from dataclasses import dataclass
from typing import ClassVar

import bookings
import movies
import storage
import seating
import reports
from seating import is_seat_available


# Start Menu/
# │
# ├── 1.Main Menu/
# │   ├── Movie Info
# │   ├── Schedule Info
# │   ├── New Booking
# │   ├── View Bookings
# │   ├── Cancel Booking
# │   └── Continue Booking
# │
# └── 2.Admin Menu/
#     ├── Add Movie
#     ├── Remove Movie
#     ├── Add Showtime
#     ├── Remove Showtime
#     ├── Edit Showtime
#     ├── 2.1.Reports/
#     │   ├── Export Reports
#     │   ├── Occupancy Report
#     │   ├── Revenue Report
#     │   └── Top Movies Report
#     └── 2.2.Backups/
#         ├── Save Backup
#         └── Load Backup

# Done:
# Main: Schedule Viewing
# Main: Movie Details
# Main: Booking
# Admin: Movies & Showtimes
# Admin: Reporting & Analytics
# Admin: Storage & Backups


# Theater name
theater_name = "Testificate"
# Theater data
pricing_data = {
    "pricing_tiers": {
        1: 60,
        2: 100,
        3: 140,
        4: 180,
        5: 220
    },
    "tax": 20,
    "discounts": {
        "min_age": (16, 10),
        "max_age": (60, 10),
        "group": (5, 15),
        "student": ("edu", 15)}
}

booking_refund_policy = {
    "purchase_time_limit_hours": 72,  # Hours after purchase when ticket becomes non-refundable.
    "film_proximity_limit_hours": 2   # Hours until movie when ticket becomes non-refundable.
}

admin_passcode = "123"

# Database path
data_path = "./data/"
# Backup path
backup_path = "./backup/"
# Create directories if absent
os.makedirs(backup_path, exist_ok=True)
os.makedirs(data_path, exist_ok=True)
# Create data files if absent
for file_name in ["movies.json", "showtimes.json", "bookings.json"]:
    if not os.path.exists(data_path + file_name):
        with open(data_path + file_name, 'x') as new_file:
            new_file.write("[]")
# Load date into memory
storage.load_state(data_path)


@dataclass
class MenuSelector:
    """Menu prompt (str) & options (list(dict)). 'run' prints them and makes user choose (returns key)."""
    prompt_for_number: ClassVar[str] = "Enter a number: "
    number_selection_error: ClassVar[str] = "Invalid selection. Enter to continue. "
    option_page_controls: ClassVar[list[dict[str,str]]] = [{"pg_prev": "[Previous Page]"}, {"pg_next": "[Next Page]"}]
    prompt: str
    options: list[dict[str, str]]
    max_opts_per_page: int = 10

    @classmethod
    def dynamic_selector(cls, prompt: str, raw_options: list[str | dict], run_immediately: bool = True):
        """Construct new instance. Non-dict options are keyed as string-integers."""
        options = [{"back": "[Go back]"}]  # Default first option
        for index, option in enumerate(raw_options, 1):
            if type(option) == dict:
                # Append to options list.
                options.append(option)
            else:
                # Append to options list with enumerator as makeshift key.
                options.append({str(index): option})
        if run_immediately:
            return cls(prompt, options).run()
        return cls(prompt, options)

    def run(self, page: int = 0, prompt_override: str = "") -> str:
        """Displays menu until user makes a valid choice."""
        while True:
            clear_terminal()
            options = self._get_page_options(page)
            self._print_menu(options, prompt_override)
            choice = self._make_user_choose(options)
            if choice == "pg_prev":
                page -= 1
                continue
            elif choice == "pg_next":
                page += 1
                continue
            elif not choice:
                input(MenuSelector.number_selection_error)
                continue
            break
        return choice

    def _print_menu(self, options, prompt_override: str = None):
        """Prints instance's prompt & options."""
        print((self.prompt * bool(not prompt_override)) +
              (str(prompt_override) * bool(prompt_override)))  # Branchless conditional for prompt overriding
        for i, option in enumerate(options):
            if next(iter((option.values()))) == "null":
                continue
            print(f"{i}: {next(iter((option.values())))}")  # Print all options except null ones
        return

    def _make_user_choose(self, options) -> str | None:
        """Prompts user to select an option & returns it. Returns None when invalid selection."""
        if not options:
            options = self.options
        try:
            return next(iter(options[int(input(MenuSelector.prompt_for_number))].keys()))  # Return chosen key
        except (NameError, TypeError, IndexError, ValueError):
            return None

    def _get_page_options(self, page: int):
        """Get list of options to be displayed depending on page number."""
        if len(self.options) <= MenuSelector.max_opts_per_page:
            # No need for page logic.
            return self.options
        if page == 0:
            # Special case for page 0: don't do a "previous page" option.
            page_options = list(self.options[((self.max_opts_per_page - 2) * page):
                                             ((self.max_opts_per_page - 2) * (page + 1)) + 1])
            page_options.append(MenuSelector.option_page_controls[1])
        else:
            page_options = list(self.options[((self.max_opts_per_page - 2) * page) + 1:
                                             ((self.max_opts_per_page - 2) * (page + 1)) + 1])
            page_options.insert(0,MenuSelector.option_page_controls[0])
            if len(page_options) > 8 and self.options[((self.max_opts_per_page - 2) * (page + 1)) + 1:]:
                # Only print "next page" button if the menu is filled up & there are options to be printed
                page_options.append(MenuSelector.option_page_controls[1])
        return page_options


# Initialise menu selection instances
start_screen = MenuSelector(
    f"Booking System for {theater_name} Theater", [             # Startup
        {"quit": "Quit Applet"},                                # EXIT
        {"main": "Customer Menu"},                              # 1.Submenu
        {"admin": "Administrative Menu"}])                      # 2.Submenu

main_selector = MenuSelector(
    "What would you like to do?", [                             # 1.Main
        {"back": "[Exit]"},                                     # BACK
        {"imdb": "Read about available movies"},                # Action
        {"schedule": "View scheduled showings"},                # Action
        {"new_book": "Make a new booking"},                     # Action
        {"view_book": "View your existing bookings"},           # Action
        {"canc_book": "Request a refund for existing booking"}, # Action
        {"cont_book": "Continue booking process"}])             # Action


admin_selector = MenuSelector(
    "What would you like to manage?", [                         # 2.Admin
        {"back": "[Exit]"},                                     # BACK
        {"add_movie": "Add a new movie"},                       # Action
        {"rem_movie": "Retire an existing movie"},              # Action
        {"add_showtime": "Schedule a new showing"},             # Action
        {"rem_showtime": "Retire an existing showtime"},        # Action
        {"edit_showtime": "Edit an existing showing"},          # Action
        {"reports": "View analytics"},                          # 2.1 Submenu
        {"backups": "Manage database backups"}])                # 2.2 Submenu

admin_reports_selector = MenuSelector(
    "Analytic options:", [                                      # 2.1 Admin Reports
        {"back": "[Go back]"},                                  # BACK
        {"export": "Export all analytics to file"},             # Action
        {"occupancy": "View occupancy statistics"},             # Action
        {"revenue": "View revenue summary"},                    # Action
        {"top_movies": "View the most popular 5 movies"}])      # Action

admin_backups_selector = MenuSelector(
    "Backup options:", [                                        # 2.2 Admin Backups
        {"back": "[Go back]"},                                  # BACK
        {"save_backup": "Create a manual backup of data"},      # Action
        {"load_backup": "Load a saved backup file."}])          # Action


### Menus
def start_menu():
    """Menu to be shown upon launching the script."""
    while True:
        match start_screen.run():
            case "quit":
                quit()
            case "main":
                main_menu()
            case "admin":
                if getpass.getpass("Enter Passcode: ") != admin_passcode:
                    print("Invalid passcode.")
                else:
                    admin_menu()
            case _:
                raise NotImplementedError
        pause_confirm()

def main_menu():
    """Main menu for customers."""
    while True:
        choice = main_selector.run()
        storage.load_state(data_path)
        match choice:
            case "back":
                return
            case "imdb":
                if movie := dynamic_select_movie("Select a movie to learn more about it: "):
                    print(movie.pretty_string())
            case "schedule":
                if (search_term := input("Enter date/title to search, or blank to view all: ").lower().strip()) != "q":
                    print_list(movies.list_showtimes(search_term, only_future=True))
            case "new_book":
                booking_process_handler()
                storage.save_state(data_path)
            case "view_book":
                if (search_email := input("Enter your email ('q' to go back): ").lower().strip()) != "q":
                    print_list(bookings.list_customer_bookings(search_email), True)
            case "canc_book":
                if (booking_id := input("Enter the booking ID you'd like to cancel: ").lower().strip()) != "q":
                    bookings.cancel_booking(booking_id, booking_refund_policy)
                    storage.save_state(data_path)
            case "cont_book":
                if (reserve_id := input("Enter code ('q' to go back): ").lower().strip()) != "q":
                    cont_booking_action(reserve_id)
                    storage.save_state(data_path)
            case _:
                raise NotImplementedError
        pause_confirm()


def admin_menu():
    """Main menu for admins."""
    while True:
        choice = admin_selector.run()
        storage.load_state(data_path)
        match choice:
            case "back":
                return
            case "add_movie":
                movies.add_movie()
                storage.save_state(data_path)
            case "rem_movie":
                if movie := dynamic_select_movie("Select a movie to retire:"):
                    movies.remove_movie(movie)
                    storage.save_state(data_path)
            case "add_showtime":
                if movie := dynamic_select_movie("Select a movie to schedule a new showing for: "):
                    movies.schedule_showtime(movie)
                    storage.save_state(data_path)
            case "rem_showtime":
                if showing := dynamic_select_showtime("Select a showing to retire: "):
                    movies.remove_showtime(showing)
                    storage.save_state(data_path)
            case "edit_showtime":
                if showing := dynamic_select_showtime("Select a showing to edit:"):
                    movies.update_showtime(showing)
                    storage.save_state(data_path)
            case "reports":
                admin_reports_menu()
            case "backups":
                admin_backups_menu()
            case _:
                raise NotImplementedError
        pause_confirm()

def admin_reports_menu():
    """Admin menu to view and export analytics"""
    while True:
        choice = admin_reports_selector.run()
        storage.load_state(data_path)
        match choice:
            case "back":
                return
            case "export":
                if filename := input("Enter name for export file: ").strip():
                    movies_list = list(movies.Showtime.current_items.values())
                    bookings_list = list(bookings.Booking.current_items.values())
                    reports.export_report(filename, movies_list, bookings_list)
            case "occupancy":
                showtime_list = list(movies.Showtime.current_items.values())
                print_dict(reports.occupancy_report(showtime_list))
            case "revenue":
                bookings_list = list(bookings.Booking.current_items.values())
                showtime_list = list(movies.Showtime.current_items.values())
                if dates := input("Enter date range (space-separated) (blank for automatic range): ").lower().strip():
                    if len(dates := [date.strip() for date in dates.split("-")]) != 2:
                        print("Error: Must enter two space-separated dates (YYYY-MM-DD YYYY-MM-DD).")
                        continue
                    try:
                        dates = [dt.datetime.strptime(date, "%Y-%m-%d") for date in dates]
                    except ValueError:
                        print("Error: Dates must be formatted as YYYY-MM-DD")
                        continue
                print_dict(reports.revenue_summary(bookings_list, showtime_list, dates))
            case "top_movies":
                print_list(reports.top_movies(list(movies.Showtime.current_items.values())))
            case _:
                raise NotImplementedError
        pause_confirm()

def admin_backups_menu():
    """Admin menu to load/save backups"""
    while True:
        choice = admin_backups_selector.run()
        storage.load_state(data_path)
        match choice:
            case "back":
                return
            case "save_backup":
                storage.backup_state(backup_path)
            case "load_backup":
                storage.load_backup(backup_path, data_path)
            case _:
                raise NotImplementedError
        pause_confirm()



# Menu Helper Functions--------------------------------------------

def booking_process_handler(reservation: bookings.Booking = None):
    """Create a booking."""
    # Get seating and showing from 'reservation'; prompt the user if no reservation.
    if not (showing := dynamic_select_showtime(only_future=True) if not reservation else reservation.showtime):
        return  # Showtime selection aborted by user
    if not (seats := seating.select_seats(showing) if not reservation else reservation.seats):
        return  # Seat selection aborted by user
    reservation = seating.reserve_seats(seats, showing, bookings.Booking) if not reservation else reservation
    # Do payment.
    if not bookings.payment(booking_data := bookings.new_booking(showing, seats, pricing_data)):
        print(f"Payment cancelled by user.")
        if reserve_time_left := (reservation.max_reserve_mins - reservation.minutes_since_issued) >= 1:
            # Tell user that they can continue booking later if their seats are still reserved.
            print(f"Seats reserved for {reserve_time_left:.01f} minutes.\n"
                  f"Use code to continue booking: {reservation.uid}")
        return
    elif not is_seat_available(seats, showing, reservation):
        print("Your payment has been cancelled.")
        return  # User's seats are no longer available
    print("Payment successful.")
    reservation.remove_self()  # Booking complete: delete reservation
    del reservation
    bookings.generate_ticket(booking_data)


def cont_booking_action(reserve_id: str):
    """Asks for reservation code; returns reservation (and refreshes its duration) if valid."""
    if (not reserve_id) or (reserve_id == "q"):
        return  # Process aborted by user.
    reservation = bookings.Booking.current_items.get(reserve_id, None)
    if (not reservation) or reservation.confirmed:
        print("Invalid code!")
        return  # No such reservation exists.
    elif reservation.minutes_since_issued >= reservation.max_reserve_mins:
        print("Code has expired!")
        reservation.remove_self()
        del reservation
        return  # Reservation has expired (and now deleted).
    else:
        # Valid reservation: refresh its duration and continue booking process.
        seats, showing = reservation.seats, reservation.showtime
        reservation.remove_self()
        del reservation
        refreshed_reservation = seating.reserve_seats(seats, showing, bookings.Booking, reserve_id)
        print(f"Continuing booking for {showing.pretty_string(short=True)}")
        booking_process_handler(refreshed_reservation)



# General Purpose Functions---------------------

def dynamic_select_movie(prompt: str) -> movies.Movie | None:
    """Summon a menu where the user can pick a movie."""
    temp_movie_dict = movies.Movie.current_items.copy()  # Cache it in case movies are edited during choice
    user_choice = MenuSelector.dynamic_selector(
        prompt,
        [{key: value.title} for key, value in temp_movie_dict.items()]
    )
    if user_choice == "back":
        return None
    return temp_movie_dict[user_choice]

def dynamic_select_showtime(prompt: str = "", only_future: bool = False) -> movies.Showtime | None:
    """Summon a menu where the user can pick a showtime."""
    
    if not prompt:
        prompt = "Select a scheduled showing: "
    temp_showtime_dict = movies.Showtime.current_items.copy()  # Cache it in case edited during choice
    if only_future:
        showtimes = [{key: value.pretty_string()} for key, value in temp_showtime_dict.items() if value.datetime > dt.datetime.now()]
    else:
        showtimes = [{key: value.pretty_string()} for key, value in temp_showtime_dict.items()]
    user_choice = MenuSelector.dynamic_selector(
        prompt,
        showtimes
    )
    if user_choice == "back":
        return None
    return temp_showtime_dict[int(user_choice)]

def clear_terminal():
    """Clear the terminal"""
    if os.name == "nt":
        os.system("cls")  # Windows
    else:
        os.system("clear")  # Unix/-Like

def pause_confirm():
    """Hold the screen until user presses enter"""
    input("[Enter to continue] ")

def print_list(my_list: list, double_spaced = False):
    """Print a given list with optional double-spacing. Custom classes are printed using pretty_string method."""
    if not my_list:
        return
    if all(isinstance(item, (bookings.Booking, movies.Movie, movies.Showtime)) for item in my_list):
        # If they're all custom objects, use the pretty_string method.
        if double_spaced:
            [print(f"\n{item.pretty_string()}") for item in my_list]
            print()
        else:
            [print(item.pretty_string()) for item in my_list]
    else:
        if double_spaced:
            [print(f"\n{item}") for item in my_list]
            print()
        else:
            [print(item) for item in my_list]

def print_dict(my_dict: dict, double_spaced: bool = False, dynamic_key_char_limit = True, key_char_limit: int = 20):
    """Print a given dictionary object."""
    if dynamic_key_char_limit:
        key_char_limit = max([len(key) for key in my_dict])
    if double_spaced:
        [print(f"\n{_text_padding_shortening(key.title(), key_char_limit)}\t:\t{value}") for key, value in my_dict.items()]
        print()
    else:
        [print(f"{_text_padding_shortening(key.title(), key_char_limit)}\t:\t{value}") for key, value in my_dict.items()]

def _text_padding_shortening(my_string: str, char_limit: int) -> str:
    if char_limit <= 2:
        raise ValueError("Limit too low")
    if len(my_string) <= char_limit:
        return my_string + (" " * (char_limit - len(my_string)))
    return my_string[:char_limit - 2] + "…" + my_string[-1]


# START
start_menu()
