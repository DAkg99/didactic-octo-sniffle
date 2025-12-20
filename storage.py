"""
    Validates actions, saves & loads database and backups.
"""

import datetime as dt

import bookings
import movies

def payment(price: int):
    """Pretend to take payments"""
    print(f"Your total is {price}₺")
    input("Enter payment details: ")
    return True

def user_input_verified_date(prompt_override: str = "") -> dt.datetime | None:
    """Repeatedly prompts user for valid string until one is given (return datetime) or user cancels (return None)"""
    # Branchless conditional to determine prompt string, followed by loop to get valid answer from user
    prompt = (f"Enter date (YYYY-MM-DD): " * bool(not prompt_override)  + prompt_override * bool(prompt_override))
    while True:
        try:
            return dt.datetime.strptime(input(prompt), "%Y-%m-%d")
        except ValueError:
            if input("Invalid date. Enter to try again, 'q' to cancel: ").strip().lower() == "q":
                return None

def load_state(path: str):
    movies.load_movies(path)
    movies.load_showtimes(path)
    bookings.load_bookings(path)

def save_state(path: str):
    movies.save_movies(path)
    movies.save_showtimes(path)
