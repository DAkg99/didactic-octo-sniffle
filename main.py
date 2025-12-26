import os
import datetime as dt
from dataclasses import dataclass
from typing import ClassVar



import bookings
import movies
import storage
import seating
import reports

# Main Menu/
# ├── Admin Menu/
# │   └── ...
# ├── Schedule Viewing Menu/
# │   ├── Search by title
# │   ├── Search by date
# │   └── Show all
# ├── Booking Menu/
# │   ├── New Booking
# │   ├── View Bookings
# │   └── Delete Booking
# └── View Movie Details
#
# Main Menu/
# └── Admin Menu/
#     ├── Movies & Showtimes Menu/
#     │   ├── New Movie
#     │   ├── Remove Movie
#     │   ├── New Showtime
#     │   ├── Edit Showtime
#     │   └── Remove Showtime
#     ├── Reports Menu/
#     │   ├── Export to file
#     │   ├── View occupancy
#     │   ├── View revenue
#     │   └── View most popular
#     └── Backups Menu/
#         └── Create Backup


# Done:
# Main: Schedule Viewing
# Main: Movie Details
# Main: Booking
# Admin: Movies & Showtimes
# Admin: Reporting & Analytics
# Admin: Storage & Backups

# Working on:
# General clean up
# Move reservation logic completely to booking. Reserved seats should be 'unconfirmed' bookings.
# Fix booking printing

# To-do:
# Seating: Map: Add legend
# Admin: Movies & Showtimes: Prevent overlapping screenings (storage.validate_showtime()).
# Main: Booking: New: Tell user that they already booked for showtime & ask to confirm.
# Main: Booking: New: Differentiate "reserved" and "sold" in seat map.
# Admin: Reporting & Analytics: Export: Disallow illegal file characters maybe.
# Main: Schedule Viewing: Pretty Print
# Admin: Passcode Protection
# Remove hardcoded workarounds for os.get_terminal_size(). Marked with debug comments


# Extra To-dos:
# General: Put load_state() before any action that is about to save state, so they change the most recent date.
# Main: Booking: Instead of running a timer, save reserved seats with the time they're issued at. When fetching
#  reserved seats, ones older than X minutes can automatically be deleted.
# Main: Booking menu: New: Add a ----screen---- line to seat map.
# Main: Schedule Viewer: Send user to create new booking.
# Main: Schedule Viewer: Non-exact search for movie title.
# Different room sizes for different screens
# Check for duplicates in movie/booking database, automatically remove them
# Instead of storing all bookings in memory, only store their ids for look-ups.
# Colored terminal
# Clear terminal between prompts
# Admin: Reporting/Analytics: Export: CSV

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
# Load everything in
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
    def dynamic_selector(cls, prompt: str, raw_options: list, run: bool = True):
        """Construct instance with options. Non-dict options are keyed as string-integers."""
        options = [{"back": "[Go back]"}]  # First option
        for index, option in enumerate(raw_options, 1):
            if type(option) == dict:
                options.append(option)  # Use dict key as the option value if it's a dict, use enumerated key otherwise.
            else:
                options.append({str(index): option})
        if run:
            return cls(prompt, options).run()
        return cls(prompt, options)

    def run(self, page: int = 0, prompt_override: str = "") -> str:
        """Displays menu until user makes a valid choice."""
        while True:
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
        """Prints instance's prompt & options. Prompt can be overridden."""
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
        if len(self.options) <= MenuSelector.max_opts_per_page:
            page_options = self.options
        elif page == 0:
            page_options = list(self.options[((self.max_opts_per_page - 2) * page):((self.max_opts_per_page - 2) * (page + 1))+1])
            page_options.append(MenuSelector.option_page_controls[1])
        else:
            page_options = list(self.options[((self.max_opts_per_page - 2) * page) + 1:((self.max_opts_per_page - 2) * (page + 1))+ 1])
            page_options.insert(0,MenuSelector.option_page_controls[0])
            while len(page_options) < 9:
                page_options.append({"":"null"})
            page_options.append(MenuSelector.option_page_controls[1])
        return page_options


# Initialise menu selection objects
main_selector = MenuSelector(
    "What would you like to do?", [                         # 1.Main
        {"admin": "[Staff Access]"},                        # 1.Submenu
        {"schedule": "View scheduled showtimes"},           # 2.Submenu
        {"book": "Manage booking"},                         # 3.Submenu
        {"imdb": "Read more about available movies"}])      # 4.Submenu

schedule_selector = MenuSelector(
    "How would you like to view the schedule?", [           # 1.2 Schedule Showings
        {"back": "[Go back]"},                              # BACK
        {"title": "Showings of a specific movie"},          # Action
        {"date": "Showings at a specific date"},            # Action
        {"all": "All showings"}])                           # Action

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
        {"new_movie": "Add a new movie"},                   # Action
        {"rem_movie": "Retire a movie"},                    # Action
        {"new_showing": "Add new showing to schedule"},     # Action
        {"edit_showing": "Edit existing showing"},          # Action
        {"rem_showing": "Remove a showing from schedule"}]) # Action

admin_reports_selector = MenuSelector(
    "Analytic options:", [                                  # 1.1.2 Admin Reports
        {"back": "[Go back]"},                              # BACK
        {"export": "Export all analytics to file"},         # Action
        {"occupancy": "View occupancy statistics"},         # Action
        {"revenue": "View revenue summary"},                # Action
        {"top_movies": "View the most popular 5 movies"}])  # Action

admin_backups_selector = MenuSelector(
    "Backup options:", [                                    # 1.1.3 Admin Backups
        {"back": "[Go back]"},                              # BACK
        {"save_backup": "Create a manual backup of data"},  # Action
        {"load_backup": "Load a saved backup file."}])      # Action
        #{"": ""},
        #{"": ""}])


### Menus
def main_menu():
    clear_terminal()
    while True:
        match main_selector.run():
            case "admin":
                admin_menu()
            case "schedule":
                schedule_menu()
            case "book":
                book_menu()
            case "imdb":
                movie_details_action()
                pause_confirm()
            case _:
                raise NotImplementedError

def schedule_menu():
    """Make user search through the schedule"""
    clear_terminal()
    while True:
        match schedule_selector.run():
            case "back":
                return
            case "title":
                if search_for := input(f"Enter movie title: "):
                    print_list(movies.list_showtimes(search_for))
            case "date":
                if search_for := storage.user_input_verified_date("date"):
                    print_list(movies.list_showtimes(search_for))
            case "all":
                print_list(movies.list_showtimes())
            case _:
                raise NotImplementedError
        pause_confirm()

def book_menu():
    """Get user to view and manage bookings"""
    clear_terminal()
    while True:
        match book_selector.run():
            case "back":
                return
            case "new_book":
                new_booking_action()
            case "view_book":
                view_booking_action()
            case "remove_book":
                remove_booking_action()
            case _:
                raise NotImplementedError
        storage.save_state(data_path)
        pause_confirm()

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
                raise NotImplementedError

def admin_movies_menu():
    """Admin menu to manage movies and showings"""
    while True:
        match admin_movies_selector.run():
            case "back":
                return
            case "new_movie":
                admin_new_movie_action()
            case "rem_movie":
                admin_remove_movie_action()
            case "new_showing":
                admin_new_showing_action()
            case "edit_showing":
                admin_edit_showing_action()
            case "rem_showing":
                admin_remove_showing_action()
            case _:
                raise NotImplementedError
        pause_confirm()
        storage.save_state(data_path)

def admin_reports_menu():
    """Admin menu to view and export analytics"""
    while True:
        match admin_reports_selector.run():
            case "back":
                return
            case "export":
                admin_reports_export_action()
            case "occupancy":
                admin_reports_occupancy_action()
            case "revenue":
                admin_report_revenue_action()
            case "top_movies":
                admin_report_top_action()
            case _:
                raise NotImplementedError
        pause_confirm()

def admin_backups_menu():
    """Admin menu to export backups"""
    while True:
        match admin_backups_selector.run():
            case "back":
                return
            case "save_backup":
                storage.backup_state(backup_path)
            case "load_backup":
                storage.load_backup(backup_path, data_path)
            case _:
                raise NotImplementedError
        storage.save_state(data_path)
        pause_confirm()


# Actions--------
## Main Menu Actions----
def movie_details_action():
    movie = dynamic_select_movie("Select a movie to learn more about it:")
    if not movie:
        return
    movie_pretty_print(movie)

### Booking Actions-----
def new_booking_action():
    showing = dynamic_select_showtime("Select a scheduled showing:")
    if not showing:
        return
    seats, reserve_id = seating.select_seats(showing)  # Select seats
    if not seats:
        return
    booking_data = bookings.new_booking(showing, seats["tuple"], pricing_data)  # Generate booking data
    if bookings.payment(booking_data["cost"], showing, seats["formatted"], reserve_id):
        bookings.generate_ticket(booking_data)  # Generate ticket if payment success

def view_booking_action():
    search_email = input("Enter your email ('q' to go back): ").lower().strip()
    if search_email == "q":
        return
    print_list(bookings.list_customer_bookings(search_email), True)

def remove_booking_action():
    booking_id = input("Enter the booking ID you'd like to cancel ('q' to go back): ").strip().lower()
    if booking_id == "q":
        return
    bookings.cancel_booking(booking_id, booking_refund_policy)

## Admin Movie Actions-----
def admin_new_movie_action():
    movies.add_movie()

def admin_remove_movie_action():
    movie = dynamic_select_movie("Select a movie to retire:")
    if not movie:
        return
    movies.remove_movie(movie)

def admin_new_showing_action():
    admin_choice = MenuSelector.dynamic_selector(
        "Select a movie to create a showing for:",
        cached_movies := [movie for movie in movies.Movie.current_items.values()])
    if admin_choice == "back":
        return
    showing_movie = cached_movies[int(admin_choice) - 1]
    movies.schedule_showtime(showing_movie)

def admin_edit_showing_action():
    showing = dynamic_select_showtime("Select a showing to edit:")
    if not showing:
        return
    movies.update_showtime(showing)

def admin_remove_showing_action():
    admin_choice = MenuSelector.dynamic_selector(
        "Select a showing to retire:",
        cached_showings := [showing for showing in movies.Showtime.current_items.values()])
    if admin_choice == "back":
        return
    retired_showing = cached_showings[int(admin_choice) - 1]
    movies.remove_showtime(retired_showing)

### Admin Reports Actions
def admin_reports_export_action():
    reports.export_report(input("filename:"), list(movies.Showtime.current_items.values()),
                          list(bookings.Booking.current_items.values()))

def admin_reports_occupancy_action():
    occupancy_data = reports.occupancy_report(list(movies.Showtime.current_items.values()))
    print_dict(occupancy_data)

def admin_report_revenue_action():
    mode = input("Enter date range manually, or automatically set widest possible range? (m/a): ").lower().strip()
    if mode == "m":
        print("Please provide the range of dates you would like to query.")
        date1 = storage.user_input_verified_date("date", "Enter first date: ")
        if not date1:
            return
        date2 = storage.user_input_verified_date("date", "Enter second date: ")
        if not date2:
            return
        revenue_data = reports.revenue_summary(list(bookings.Booking.current_items.values()), (date1, date2))
    else:
        revenue_data = reports.revenue_summary(list(bookings.Booking.current_items.values()), None,
                                               list(movies.Showtime.current_items.values()))
    print_dict(revenue_data)

def admin_report_top_action():
    print_list(reports.top_movies(list(movies.Showtime.current_items.values())))


# General Purpose Functions---------
def dynamic_select_movie(prompt: str) -> movies.Movie | None:
    temp_movie_dict = movies.Movie.current_items.copy()  # Cache it in case movies are edited during choice
    user_choice = MenuSelector.dynamic_selector(
        prompt,
        [{key: value.title} for key, value in temp_movie_dict.items()]
    )
    if user_choice == "back":
        return None
    return temp_movie_dict[user_choice]

def dynamic_select_showtime(prompt: str) -> movies.Showtime | None:
    temp_showtime_dict = movies.Showtime.current_items.copy()  # Cache it in case edited during choice
    user_choice = MenuSelector.dynamic_selector(
        prompt,
        [{key: value.pretty_string()} for key, value in temp_showtime_dict.items()]
    )
    if user_choice == "back":
        return None
    return temp_showtime_dict[int(user_choice)]

def clear_terminal():
    if os.name == "nt":
        os.system("cls")  # Windows
    else:
        os.system("clear")  # Unix & Unix-Like

def pause_confirm():
    input("[Enter to continue] ")

def print_list(my_list: list, double_spaced = False):
    if not my_list:
        return
    # If they're all custom objects, use existing method to get pretty string.
    # Otherwise, print them normally.
    if all(isinstance(item, (bookings.Booking, movies.Movie, movies.Showtime)) for item in my_list):
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
    if dynamic_key_char_limit:
        key_char_limit = max([len(key) for key in my_dict])
    if double_spaced:
        [print(f"\n{text_padding_shortening(key.title(), key_char_limit)}\t:\t{value}") for key, value in my_dict.items()]
        print()
    else:
        [print(f"{text_padding_shortening(key.title(), key_char_limit)}\t:\t{value}") for key, value in my_dict.items()]

def text_padding_shortening(my_string: str, char_limit: int) -> str:
    if char_limit <= 2:
        raise ValueError("Limit too low")
    if len(my_string) <= char_limit:
        return my_string + (" " * (char_limit - len(my_string)))
    return my_string[:char_limit - 2] + "…" + my_string[-1]

def center_string_x(my_str: str, min_padding: int = 0, min_lines: int = 0, pad_char: str = " ") -> str:
    """
        Centers string horizontally on the terminal by padding its left and right side with characters.
        Splits string into lines to fit better, or to abide by min_lines argument (atg must be >= number of words).
        Minimum padding argument isn't respected if terminal too narrow.
        If terminal is still too narrow, function is nulled and input is returned without processing.
    """
    # terminal_width = next(iter(os.get_terminal_size()))
    terminal_width = 120    # DEBUG
    min_width_allowed = 5   # Keep this 3 or higher
    if terminal_width < min_width_allowed:
        return my_str       # Null function; terminal too narrow
    if min_lines > len(my_str.split()):
        raise Exception(f"Input string has too few space-separated words to be split into {min_lines} lines.")

    while terminal_width - min_padding < min_width_allowed:  # Decrease min_padding if necessary
        min_padding -= 1
    working_columns = terminal_width - min_padding
    my_str = my_str.strip()
    # Recursively go through the string. Divide into words or hyphenated chunk when necessary.
    if working_columns < len(my_str):
        if len(my_str.split()) > 1:
            return "\n".join([center_string_x(word, min_padding, min_lines, pad_char)
                              for word in my_str.split()])
        return "\n".join([center_string_x(chunk, min_padding, min_lines, pad_char)
                          for chunk in string_spread_to_chunks(my_str, working_columns)])
    # Set left and right padding
    padding_left = (terminal_width - len(my_str)) // 2 * pad_char
    if pad_char == " ":
        padding_right = "" # Don't bother with right padding if pad_char is space anyway.
    else:
        # Padding_right subtracts 1 at the end, otherwise Windows CMD does line-breaks.
        padding_right = ((terminal_width - len(my_str)) // 2  + ((terminal_width - len(my_str)) % 2 - 1)) * pad_char
    return padding_left + my_str + padding_right

def string_spread_to_chunks(my_str: str, max_chunk_size: int, hyphenate: bool = True) -> list[str]:
    """Splits string into relatively even chunks, abiding by the max chunk size given"""
    bin_count = len(my_str) // (max_chunk_size - (1 * hyphenate)) + 1
    min_chunk_size = (len(my_str)//bin_count)
    remainder = len(my_str) % bin_count
    string_chunks = []
    for i in [_ * min_chunk_size + remainder for _ in range(0, bin_count)]: # Ignores the first remainder-many chars.
        string_chunks.append(my_str[i:(i + min_chunk_size)] + ("-" * hyphenate))
    string_chunks[0] = my_str[0:remainder] + string_chunks[0] # Ignored chars are added to the first bin.
    string_chunks[-1] = string_chunks[-1][0:-1] if hyphenate else string_chunks[-1] # Last hyphen removed.
    return string_chunks


# Movie Details Functions---------
def movie_pretty_print(movie: movies.Movie):
    print(f"Title: {movie.title}\n"
          f"Genre: {', '.join(list(map(str, movie.genre))).capitalize()}\n"
          f"Duration: {str(movie.duration.seconds//3600)}H{str(movie.duration.seconds//60)}M\n"
          f"Rating: {movie.rating:.2f}/5.00\n"
          f"Description: {movie.description}")




# START
clear_terminal()
print(center_string_x(f"Welcome to {theater_name}!"),"\n")
main_menu()
