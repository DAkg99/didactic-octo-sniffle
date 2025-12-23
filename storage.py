"""
    Validates actions, saves & loads database and backups.
"""

import datetime as dt

import bookings
import movies



def user_input_verified_date(mode: str = "datetime", prompt_override: str = "") -> dt.datetime | None:
    """Repeatedly prompts user for valid string until one is given (return datetime) or user cancels (return None)
    Despite the mode argument, all returned values are datetime rather than date or time."""
    formatting = "%Y-%m-%d %H:%M"
    user_help_string = "YYYY-MM-DD HH:MM"
    match mode:
        case "datetime":
            formatting = "%Y-%m-%d %H:%M"
            user_help_string = "YYYY-MM-DD HH:MM"
        case "date":
            formatting = "%Y-%m-%d"
            user_help_string = "YYYY-MM-DD"
        case "time":
            formatting = "%H:%M"
            user_help_string = "HH:MM"
        case _:
            raise ValueError(f"invalid mode: {mode}")
    # Branchless conditional to determine prompt string, followed by loop to get valid answer from user
    prompt = (f"Enter date: " * bool(not prompt_override)
              + prompt_override * bool(prompt_override))
    while True:
        print(f"Date format: {user_help_string} | Type 'now' to get the current date | 'q' or blank to cancel")
        user_in = input(prompt).lower().strip()
        if (not user_in) or (user_in == "q"):
            return None
        elif user_in == "now":
            return dt.datetime.now()
        else:
            try:
                return dt.datetime.strptime(user_in, formatting)
            except (ValueError, TypeError):
                print("Invalid format.")


def load_state(path: str):
    movies.load_movies(path)
    movies.load_showtimes(path)
    bookings.load_bookings(path)

def save_state(path: str):
    movies.save_movies(path)
    movies.save_showtimes(path)
    bookings.save_bookings(path)
