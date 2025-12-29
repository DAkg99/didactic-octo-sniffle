"""
    Validates actions, saves & loads database and backups.
"""

import datetime as dt
import json
import os
import random
from collections.abc import Container

# Required internal imports for saving/loading:
import bookings
import movies

movie_data_key = "Movie Data"
showtime_data_key = "Showtime Data"
booking_data_key = "Booking Data"

def random_uid_generator(existing_uids: Container, length: int = 8) -> str:
    """Generates a hex string 'length' characters long. String is unique within the list provided."""
    uid_trial = f"{random.randint(1, (16 ** length) - 1):0{length}x}"
    while uid_trial in existing_uids:
        uid_trial = f"{random.randint(1, (16 ** length) - 1):0{length}x}"
    return uid_trial


def validate_showtime(new_showtime_data: dict):
    new_screen = new_showtime_data["screen"]
    new_start = dt.datetime.strptime(new_showtime_data["datetime"], "%Y-%m-%d %H:%M")
    new_end = new_start + movies.Movie.current_items.get(new_showtime_data["movie_id"]).duration
    for showtime in movies.Showtime.current_items.values():
        if not showtime.screen == new_screen:
            pass
        elif new_start < showtime.datetime and not (new_end < showtime.datetime):
            # There exists a showing which begins before this new one ends.
            print(f"New showing would conflict with:\n {showtime.pretty_string(short=True)}\nAborting...")
            return False
        elif new_start >= showtime.datetime and not (new_start >= showtime.datetime + showtime.movie.duration):
            # New showing begins before an older one ends.
            print(f"New showing would conflict with:\n {showtime.pretty_string(short=True)}\nAborting...")
            return False
    return True


def load_state(path: str):
    movies.load_movies(path)
    movies.load_showtimes(path)
    bookings.load_bookings(path)

def save_state(path: str):
    movies.save_movies(path)
    movies.save_showtimes(path)
    bookings.save_bookings(path)

def backup_state(backup_path: str):
    datetime_str = dt.datetime.now().strftime("%Y%m%d%H%M")
    backup_data = {
        movie_data_key: [movie.to_dict() for movie in movies.Movie.current_items.values()],
        showtime_data_key: [showtime.to_dict() for showtime in movies.Showtime.current_items.values()],
        booking_data_key: [booking.to_dict() for booking in bookings.Booking.current_items.values()]
    }
    with open(fullpath := f"{backup_path}backup-{datetime_str}.json", "w") as exp_file:
        json.dump(backup_data, exp_file, indent=4)
        print(f"Exported data to {fullpath}")

def load_backup(backup_path: str, data_path: str):
    #  If possible, print most recent backup files for user convenience.
    if files := [file.name for file in os.scandir(backup_path) if file.is_file()]:
        print_count = 5
        print(f"{print_count} most recent backup files: ")
        for count, file_name in enumerate(files[::-1], 1):
            print(file_name)
            if count > print_count:
                break
    #  Get and process user input (filename). Load backup file data.
    file_name = input("Enter backup file name: ").lower().strip()
    if file_name[-5:] != ".json":
        file_name += ".json"
    if not os.path.exists(f"{backup_path}{file_name}"):
        print(f"No file called {file_name} exists in directory {backup_path}.")
        return
    with open(fullpath := f"{backup_path}{file_name}", "r") as imp_file:
        data = json.load(imp_file)
    #  Replace database files with backup data.
    with open(f"{data_path}movies.json", "w") as m_f:
        json.dump(data[movie_data_key], m_f, indent=4)
    with open(f"{data_path}showtimes.json", "w") as s_f:
        json.dump(data[showtime_data_key], s_f, indent=4)
    with open(f"{data_path}bookings.json", "w") as b_f:
        json.dump(data[booking_data_key], b_f, indent=4)

    load_state(data_path)
    print(f"Imported data from {fullpath}.")
