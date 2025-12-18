import os
import datetime as dt
from dataclasses import dataclass
from typing import ClassVar
from threading import Timer

import bookings
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

# Working on:
# Booking
## Seat decoder
## Note: Remove 1-indexing from decoded seats. Only "encoded" i.e. formatted seats should have 1-indexing for num part.
## Booking class (booking.py)

# To-do:
# All unimplemented main features
# Schedule viewer pretty print
# Admin menu protection
# Admin booking cancellation
# Remove hardcoded workarounds for os.get_terminal_size(). Marked with debug comments

# Extra To-dos:
# Get rid of dogwater text-centering function
# Replace movie_pretty_print() with __repr__ method for Movie class
# Check for duplicates in database, automatically remove them
# Look up why it's probably not a good idea to do a dictionary where keys and values are the same
# Make schedule viewer send user directly to new booking, with data of requested showtime
# Colored terminal
# Clear terminal between prompts
# Prevent overlapping screenings (lol)

# Theater name
theater_name = "Testificate"
# Theater discounts
pricing_dict = {
    "price": 100,
    "tax": 20,
    "discounts": {
        "min_age": (16, 10),
        "max_age": (60, 10),
        "group": (5, 15),
        "student": ("edu", 15)
    }
}
# Database path
data_path = "./data/"
# Backup path
backup_path = "./backup/"
# Create directories if absent
os.makedirs(backup_path, exist_ok=True)
os.makedirs(data_path, exist_ok=True)
# Load everything for the first time
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
        """Construct new instance using raw_options as options (keyed as string integers). Immediately runs selection"""
        options = [{"back": "[Go back]"}]
        for index, option in enumerate(raw_options, 1):
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
        except (NameError, TypeError, IndexError):
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
                book_new_menu()
            case "view_book":
                # Placeholder
                print("TO DO")
            case "remove_book":
                # Placeholder
                print("TO DO")
            case _:
                raise NotImplemented

def book_new_menu(): # Incomplete
    while True:
        user_choice = MenuSelector.dynamic_selector(
            "Select a scheduled showing:",
            cached_showings := [showing for showing in movies.list_showtimes(data_path)])
        if user_choice == "back":
            return
        booking_dict = dict()
        showtime = cached_showings[int(user_choice) - 1]
        booking_dict["showtime_id"] = showtime.uid
        booking_dict["seats"] = ", ".join(select_seats(showtime))
        if not booking_dict["seats"]:
            continue
        booking_dict["name"], booking_dict["age"], booking_dict["email"] = ask_user_info()
        price = bookings.calculate_booking_total(pricing_dict, booking_dict)
        payment_success = storage.fake_payment(price)
        if payment_success:
            bookings.save_booking(data_path, bookings.Booking.from_dict(booking_dict))
        return

def movie_detail_menu():
    while True:
        user_choice = MenuSelector.dynamic_selector(
            "Select a movie to learn more about it:",
            cached_movies := [movie for movie in movies.Movie.current_items.values()])
        if user_choice == "back":
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
                input("Schedule showings right away? (y/n) ")
                print("Movie has been added")
                pause_confirm()
            case "rem_movie":
                # movies.remove_movie(...)
                print("[Placeholder]")
                print("Scheduled showings for this movie will also be removed")
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
                storage.save_state(data_path)  # DEBUG
            case _:
                raise NotImplemented
        pause_confirm()


# General Purpose Functions---------
def clear_terminal():
    if os.name == "nt":
        os.system("cls")  # Windows
    else:
        os.system("clear")  # Unix & Unix-Like

def pause_confirm():
    input("[Enter to continue] ")

def print_list(my_list):
    [print(item) for item in my_list]
    pause_confirm()

def ask_user_info() -> tuple[str, int, str]:
    while True: # Get name
        name = (input("Enter your full name: "))
        if not name:
            print("Name can't be blank")
            continue
        break
    while True: # Get age
        try:
            age = (int(input("Enter your age: ")))
            break
        except (TypeError, ValueError):
            print("Please enter an integer.")
    while True: # Get email
        email = input("Enter your email address: ").strip().lower()
        if email.find("@") == -1:
            print("Please enter a valid email address.")
            continue
        elif email[email.find("@"):].find(".") == -1:
            print("Please enter a valid email address.")
        else:
            break
    return name, age, email

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


# Schedule Search Functions---------
def schedule_search_title():
    if search_for := input(f"Enter movie title: "):
        print_list(movies.list_showtimes(data_path, search_for))

def schedule_search_date():
    if search_for := storage.user_input_verified_date():
        print_list(movies.list_showtimes(data_path, search_for))

def schedule_search_all():
    print_list(movies.list_showtimes(data_path))


# Movie Details Functions---------
def movie_pretty_print(movie: movies.Movie):
    print(f"Title: {movie.title}\n"
          f"Genre: {', '.join(list(map(str, movie.genre))).capitalize()}\n"
          f"Duration: {str(movie.duration.seconds//3600)}H{str(movie.duration.seconds//60)}M\n"
          f"Rating: {movie.rating:.2f}/5.00\n"
          f"Description: {movie.description}")
    pause_confirm()

# Booking Functions
def select_seats(showing: movies.Showtime):
    """Make user select seats for a given showing. Selection is validated."""
    if showing.full:
        print("This showing is full.")
        pause_confirm()
        return None
    while True:
        seat_map = seating.get_map(showing.occupied_seats, showing.seat_layout)
        seating.render_map(seat_map)
        seats = input("Enter seat or multiple seats (comma separated) ('q' to cancel): ").strip().upper().split(", ")
        if seats[0] == "Q":
            return None
        confirmed_seats = _validate_seats(seats, showing.occupied_seats, showing.seat_layout)
        if not confirmed_seats:
            continue
        reserve_id = showing.temp_reserve_seats_new(confirmed_seats)
        Timer(300, showing.temp_reserve_seats_remove, reserve_id)
        print("Your seats have been reserved for the next 5 minutes.")
        return confirmed_seats

def _validate_seats(seats: list, occupied_seats: list, seat_layout: tuple):
    """Validate given list of seats for a show. Make sure they're already clean (stripped, capitalized, etc.)"""
    final_seats = list()
    seats = list(set(seats))  # Remove duplicates
    for seat in seats:
        if not (len(seat) == 4 and seat[0:2].isalpha() and seat[2:4].isnumeric()):
            print("Error: Invalid seat format. Please try again.\n(E.g.: AB03, AB04, AB05)")
            pause_confirm()
            return None
        seat_raw = _seat_format2raw(seat)  # Seat format was correct, so we can translate into raw form
        if not ((0 <= seat_raw[0] < seat_layout[0]) and (0 < seat_raw[1] <= seat_layout[1])):
            print("Error: Seats do not exist. Please select a valid seat.")
            pause_confirm()
            return None
        if seat_raw in occupied_seats:
            print("Error: One or more of the seats you've selected are no longer available. Please pick again.")
            pause_confirm()
            return None
        final_seats.append(seat)
    return final_seats

def _seat_format2raw(seat: str) -> tuple:  # Unfinished
    """Translate formatted seat string (AA00) into seat coordinates (C, R)"""
    row = (ord(seat[0]) - 65) * 10 + (ord(seat[1]) - 65) * 1
    return row, int(seat[2:])

def _seat_raw2format(seat_raw: list) -> str:
    """Translate seat coordinates [C, R] into formatted string (AA00)"""
    row = seat_raw[0]
    left = row // 26
    right = row % 26
    left = chr(65 + left)
    right = chr(65 + right)
    return (left+right).upper() + str(seat_raw[1])


# START
clear_terminal()
print(center_string_x(f"Welcome to {theater_name}!"),"\n")
main_menu()
