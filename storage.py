"""
    Validates actions, saves & loads database and backups.
"""

import datetime as dt

import bookings
import movies



def user_input_verified_date(prompt_override: str = "") -> dt.datetime | None:
    """Repeatedly prompts user for valid string until one is given (return datetime) or user cancels (return None)"""
    # Branchless conditional to determine prompt string, followed by loop to get valid answer from user
    prompt = (f"Enter date (YYYY-MM-DD) ('q' or blank to cancel): " * bool(not prompt_override)
              + prompt_override * bool(prompt_override))
    while True:
        user_in = input(prompt).lower().strip()
        if (not user_in) or (user_in == "q"):
            return None
        else:
            try:
                return dt.datetime.strptime(user_in, "%Y-%m-%d")
            except ValueError:
                print("Invalid date. Enter to try again.")


def load_state(path: str):
    movies.load_movies(path)
    movies.load_showtimes(path)
    bookings.load_bookings(path)

def save_state(path: str):
    movies.save_movies(path)
    movies.save_showtimes(path)
    bookings.save_bookings(path)
