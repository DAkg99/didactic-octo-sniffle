"""
    Manages movies and their showtimes.
"""

import json
import datetime as dt
from dataclasses import dataclass, field
from typing import ClassVar, Self

from storage import random_uid_generator, validate_showtime

@dataclass
class Movie:
    """Class for movies which also tracks all current instances in a dict."""
    current_items: ClassVar[dict[str,Self]] = {}                  # CLASS VAR: Automatically self-populates.
    title: str
    genre: list[str] = field(compare=False)                       # Unhashable type (list)
    duration: dt.timedelta
    description: str
    rating: float = field(compare=False)                          # Attribute subject to change.
    uid: str
    showtimes: list = field(default_factory=list, compare=False)  # Unhashable type (list)

    def __post_init__(self):
        # Generate UID if none provided.
        if not self.uid:
            new_uid = random_uid_generator(self.current_items.keys())
            object.__setattr__(self, "uid", new_uid)
        # Add self to class dictionary.
        Movie.current_items[self.uid] = self

    def pretty_string(self):
        return (f"Title: {self.title}\n"
          f"Genre: {', '.join(list(map(str, self.genre))).capitalize()}\n"
          f"Duration: {str(self.duration.seconds//3600)}H{str((self.duration.seconds//60) % 60)}M\n"
          f"Rating: {self.rating:.2f}/5.00\n"
          f"Description: {self.description}")

    @property
    def editable_attribute_dict_keys(self) -> list:
        return ["title", "genre", "duration", "description", "rating"]

    @classmethod
    def from_dict(cls, movie_dict: dict[str, str | int | float | list]):
        """Create instance from dictionary."""
        if not movie_dict.get("uid"):
            movie_dict["uid"] = ""
        return cls(
            movie_dict["title"],
            movie_dict["genre"],
            dt.timedelta(minutes=(movie_dict["duration"])),
            movie_dict["description"],
            movie_dict["rating"],
            movie_dict["uid"])

    def short_title(self, limit: int = 17):
        if limit <= 2:
            raise ValueError("Limit too low")
        if len(self.title) <= limit:
            return self.title + (" " * (limit - len(self.title)))
        return self.title[:limit - 2] + "…" + self.title[-1]

    def to_dict(self):
        return {
            "title": self.title,
            "genre": self.genre,
            "duration": int((self.duration.days * 1440) + (self.duration.seconds / 60)),
            "description": self.description,
            "rating": self.rating,
            "uid": self.uid
        }

    def update_from_dict(self, data_dict: dict):
        """Updates all values except bookings"""
        self.title = data_dict["title"]
        self.genre = data_dict["genre"]
        self.duration =dt.timedelta(minutes=(data_dict["duration"]))
        self.description = data_dict["description"]
        self.rating = data_dict["rating"]

    def showtime_add(self, showtime):
        self.showtimes.append(showtime)

    def showtime_rem(self, showtime):
        self.showtimes.remove(showtime)


@dataclass
class Showtime:
    current_items: ClassVar[dict[int, Self]] = {}
    movie: Movie
    datetime: dt.datetime
    screen: int
    attendees: int
    language: str
    pricing_tier: int
    uid: int
    bookings: list = field(default_factory=list)  # Automatically populated when bookings are loaded in.
    seat_layout: tuple = (15, 10)                 # Columns, Rows
    full: bool = False                            # Automatically set.
    max_attendees: int = 0                        # Automatically set upon init.

    def __post_init__(self):
        # Sets up ID, max attendee count, and adds itself to the list of showtimes.
        self.__verify_arrangement()
        if not self.uid:
            self.uid = 0
            while True:  # Find the smallest available ID.
                self.uid += 1
                if not self.uid in list(Showtime.current_items.keys()):
                    break
        Showtime.current_items[self.uid] = self
        self.max_attendees = self.seat_layout[0] * self.seat_layout[1]
        self.movie.showtime_add(self)

    def pretty_string(self, *, short = False, title_limit = 17):
        if not short:
            return (f"{f'[{str(self.full).upper()}]' * int(self.full)}"  # [FULL] prefix if full
                f"{self.movie.short_title(title_limit)} {self.datetime.strftime('%Y %b %d %H:%M')} "
                f"(Screen: {self.screen}, Seats left: {self.max_attendees - self.attendees:03d}/{self.max_attendees} "
                f"Lang: {self.language.title()})")
        else:
            return (f"Showing: {self.movie.short_title(title_limit)} ({self.datetime.strftime('%Y %b %d %H:%M')} "
                f"Screen {self.screen} (language: {self.language.title()}))")

    @property
    def seat_cols(self) -> int:
        return self.seat_layout[1]
    @property
    def seat_rows(self) -> int:
        return self.seat_layout[0]
    @property
    def occupied_seats(self) -> dict[str, list]:
        occupied = {
            "reserved": [],
            "confirmed": []
        }
        for booking in self.bookings:
            if booking.confirmed:
                occupied["confirmed"] += booking.seats
            elif booking.minutes_since_issued < booking.max_reserve_mins:
                occupied["reserved"] += booking.seats
            else:
                # Booking is a reservation but it has expired. Delete it.
                booking.remove_self()
        return occupied
    @property
    def editable_attribute_dict_keys(self) -> list:
        return ["movie_id", "datetime", "screen", "language", "pricing_tier"]

    @classmethod
    def from_dict(cls, show_dict: dict):
        return cls(
            Movie.current_items[show_dict["movie_id"]],
            dt.datetime.strptime(show_dict["datetime"], "%Y-%m-%d %H:%M"),
            show_dict["screen"],
            0,
            show_dict["language"],
            show_dict["pricing_tier"],
            show_dict.get("uid", 0),
            show_dict.get("bookings", list())
        )

    def to_dict(self):
        return {
            "movie_id": self.movie.uid,
            "datetime": self.datetime.strftime("%Y-%m-%d %H:%M"),
            "screen": self.screen,
            "attendees": self.attendees,
            "language": self.language,
            "pricing_tier": self.pricing_tier,
            "uid": self.uid
        }

    def update_from_dict(self, data_dict: dict):
        """Updates all values except bookings"""
        self.movie = Movie.current_items[data_dict["movie_id"]]
        self.datetime = dt.datetime.strptime(data_dict["datetime"], "%Y-%m-%d %H:%M")
        self.screen = data_dict["screen"]
        self.attendees = data_dict["attendees"]
        self.language = data_dict["language"]
        self.pricing_tier = data_dict["pricing_tier"]
        self.uid = data_dict["uid"]

    def remove_self(self):
        self.movie.showtime_rem(self)
        self.current_items.pop(self.uid)

    def booking_new(self, booking):
        self.bookings.append(booking)
        self.__update_attendee_count()
        self.__update_fullness_status()

    def booking_remove(self, booking):
        self.bookings.remove(booking)
        self.__update_attendee_count()
        self.__update_fullness_status()

    def __update_attendee_count(self):
        self.attendees = len([seat for seat in [booking.seats for booking in self.bookings]])

    def __update_fullness_status(self):
        if self.attendees >= self.max_attendees:
            self.full = True
        else:
            self.full = False

    def __verify_arrangement(self):
        """Check if seat arrangement is within valid range. Raise error if not."""
        if 1 > self.seat_cols or 1 > self.seat_rows:
            raise ValueError("Seat arrangement must have positive values.")
        if self.seat_rows > 676:
            raise ValueError("Too many seats! (Too many rows to enumerate with 2 alphabetic characters)")
        elif self.seat_cols > 98:
            raise ValueError("Too many seats! (Too many columns to represent with 2 digits (1-indexed))")


# Movie functions----------------------------
def load_movies(path: str) -> list[Movie]:
    """Returns movie database as list"""
    movies_raw_list = json.load(open(path+"movies.json"))
    for item in movies_raw_list:
        Movie.from_dict(item)
    return list(Movie.current_items.values())

def save_movies(path: str) -> None:
    """Saves movies to database file"""
    with open(path+"movies.json", "w") as movies_f:
        json.dump([movie.to_dict() for movie in Movie.current_items.values()], movies_f, indent=4)

def add_movie():
    """Adds a new movie to the list of movies"""
    movie_data = _prompt_for_movie_data()
    print("\nNew movie data:\n")
    for key, value in movie_data.items():
        print(f"{key} : {value}")  # Print data for confirmation
    if input("\nConfirm new movie? (y/n): ").strip().lower() != "y":
        print("\nMovie creation aborted.")
        return
    new_movie = Movie.from_dict(movie_data)
    if _duplicate_checker(new_movie):
        print("\nError: This movie already exists. Process aborted.")
        remove_movie(new_movie, force=True)
        return
    print(f"\nNew movie created successfully:\n{new_movie.pretty_string()}\n\nDon't forget to schedule showtimes for it as well!")
    return

def remove_movie(movie: Movie, force: bool = False):
    """Remove movie. Will prompt user for confirmation if showtimes exist.
    The 'force' flag disables confirmation prompt, and suppresses the 'success' print."""
    if force:
        pass  # Don't print anything if force flag is true.
    else:
        print("\nSelected movie for removal:", movie.title)
        if movie.showtimes:
            print("WARNING: This movie has associated showtimes, which will be deleted alongside it. "
                  "This might affect your analytics.")
            if any([(showing.datetime > dt.datetime.now() and len(showing.bookings) != 0) for showing in movie.showtimes]):
                print("WARNING: This movie has future showtimes which have already been booked. It is NOT recommended to "
                      "retire this movie without refunding the customers first.")

        if input("\nRetire movie? (y/n): ").lower().strip() != "y":
            print("\nMovie deletion aborted.")
            return
    for showtime in movie.showtimes[::-1]:
        remove_showtime(showtime, True)
    Movie.current_items.pop(movie.uid)
    if not force:
        print("\nMovie deleted.")

def update_movie(movie: Movie):
    updated_data = _prompt_for_updated_movie_data(movie)
    print("\nUpdated movie data: ")
    for key, value in updated_data.items():  # Print data for confirmation.
        print(f"{key} : {value}")
    if input("\nConfirm update? (y/n): ").strip().lower() != "y":
        print("\nUpdate aborted.")
        return
    movie.update_from_dict(updated_data)
    print(f"\nUpdated movie: \n{movie.pretty_string()}\n")
    return

# Showtime functions----------------------------
def load_showtimes(path: str) -> list[Showtime]:
    """Loads showtime database file"""
    showtimes_raw_list = json.load(open(path + "showtimes.json"))
    for item in showtimes_raw_list:
        Showtime.from_dict(item)
    return list(Showtime.current_items.values())

def save_showtimes(path: str) -> None:
    """Saves showtimes to database file"""
    with open(path+"showtimes.json", "w") as showtimes_f:
        json.dump([showtime.to_dict() for showtime in Showtime.current_items.values()], showtimes_f, indent=4)

def schedule_showtime(movie: Movie):
    new_showtime_dict = _prompt_for_showtime_data(movie)
    if not validate_showtime(new_showtime_dict):
        print("\nShowtime scheduling aborted due to conflict. ")
        return
    print("\nNew showtime data:\n")
    for key, value in new_showtime_dict.items():
        print(f"{key} : {value} {bool(key == 'movie_id') * f'({movie.title})'}")  # Print data for confirmation
    if input("\nConfirm new showtime? (y/n): ").strip().lower() != "y":
        print("\nShowtime creation aborted.")
        return
    Showtime.from_dict(new_showtime_dict)
    print("\nNew showtime scheduled successfully.")

def remove_showtime(showtime: Showtime, force: bool = False):
    """Remove showtime. Will prompt user for confirmation if bookings exist.
    The 'force' flag disables confirmation prompt, and suppresses the 'success' print."""
    if force:
        pass  # Don't print anything.
    else:
        print("\nSelected:",showtime.pretty_string())  # Print selection for confirmation
        if (len(showtime.bookings) != 0) and (showtime.datetime > dt.datetime.now()):
            print(f"There are active bookings for this showtime. Retiring the showtime will delete these bookings as well.\n"
                  f"It is NOT recommended you retire this showtime without refunding the customers first.")
        elif len(showtime.bookings) != 0:
            print(f"Retiring this showtime will discard its historic booking data.")

        if input("\nProceed? (y/n): ").lower().strip() != "y":
            print("\nShowtime deletion aborted.")
            return
    for booking in showtime.bookings:
        booking.remove_self()
        del booking
    showtime.remove_self()
    del showtime
    if not force:
        print("\nShowtime deleted.")  # Don't print confirmation if force=True

def update_showtime(showtime):
    """Prompt user for new data and update showtime accordingly."""
    updated_data = _prompt_for_updated_showtime_data(showtime)
    print("\nUpdated showtime: ")
    for key, value in updated_data.items():  # Print data for confirmation.
        print(f"{key} : {value} {bool(key == 'movie_id') * f'({Movie.current_items.get(value, showtime.movie).title})'}")
    if input("\nConfirm update? (y/n): ").strip().lower() != "y":
        print("\nUpdate aborted.")
        return
    if not validate_showtime(updated_data):
        print("\nShowtime scheduling aborted due to conflict. ")
        return
    showtime.update_from_dict(updated_data)
    print(f"\nUpdated showing: \n{showtime.pretty_string()}")
    return

def list_showtimes(search_value: str | None = None, only_future: bool = False) -> list:
    """Lists showtimes. Ask_User flag determines whether function should prompt for search options."""
    # Only_future flag ensures that only future showings are shown (this is for customer convenience).
    showtimes = list(Showtime.current_items.values())
    if not search_value:
        filtered_showtimes = showtimes
        fail_string = f"No showing available."
    else:
        # Search through results. Evaluate search_value as datetime if possible; as title-string otherwise.
        filtered_showtimes = []
        try:
            search_value = dt.datetime.strptime(search_value, "%Y-%m-%d")
            fail_string = f"No showings found for date: {search_value.strftime('%Y-%m-%d')}"
            for item in showtimes:
                if item.datetime.date() == search_value.date():
                    filtered_showtimes.append(item)
        except ValueError:
            fail_string = f"No showings found for movie: {search_value}"
            for item in showtimes:
                if item.movie.title.lower() == search_value:
                    filtered_showtimes.append(item)
    if only_future:
        filtered_showtimes = [showtime for showtime in filtered_showtimes if showtime.datetime > dt.datetime.now()]
    if not filtered_showtimes:
        return [fail_string]
    return sorted(filtered_showtimes, key=lambda st: st.datetime)


# Helper functions----------------------------
def _prompt_for_movie_data() -> dict:
    new_movie = dict()
    print("Enter details for new movie:")
    new_movie["title"] = input("Movie title: ").strip().title()
    new_movie["genre"] = [genre.strip() for genre in input("Enter genre (comma-separated if multiple): ").strip().split(",")]
    new_movie["description"] = input("Enter movie description: ").strip()
    # Input duration and rating (must be type-checked).
    while True:
        duration = input("Movie duration (in integer minutes): ").strip()
        try:
            new_movie["duration"] = int(duration)
            break
        except (TypeError, ValueError, NameError):
            print("Duration must be an integer with no special characters.")
    while True:
        rating = input("Enter movie rating out of 5: ")
        try:
            new_movie["rating"] = float(rating)
            break
        except (TypeError, ValueError, NameError):
            print("Rating must be a decimal number.")
    return new_movie

def _prompt_for_showtime_data(movie) -> dict:
    print("Enter details for new showtime: ")
    new_showtime = dict()
    new_showtime["attendees"] = 0
    new_showtime["movie_id"] = movie.uid
    new_showtime["language"] = input("Enter movie language: ")
    # Get screen number
    while True:
        try:
            new_showtime["screen"] = int(input("Enter screen number: "))
            break
        except (ValueError, TypeError, NameError):
            input("Invalid screen (must be an integer).")
    # Get pricing_tier
    while True:
        try:
            new_price_tier = int(input("Enter price tier: "))
            if not (0 < new_price_tier < 6):
                input("Price tier must be between 0 and 5.")
            else:
                new_showtime["pricing_tier"] = new_price_tier
                break
        except (ValueError, TypeError, NameError):
            input("Invalid screen (must be an integer).")
    # Get datetime:
    while True:
        try:
            new_showtime["datetime"] = input("Enter date and time (YYYY-MM-DD HH:MM): ")
            dt.datetime.strptime(new_showtime["datetime"] , "%Y-%m-%d %H:%M")
            break
        except (ValueError, TypeError, NameError):
            input("Invalid date/time format.")
    return new_showtime

def _prompt_for_updated_movie_data(movie: Movie) -> dict:
    print("Updating movie: ")
    movie_data = movie.to_dict()
    for key in movie.editable_attribute_dict_keys:
        while True:
            # Print current value of key for convenience.
            print(f"\nCurrent {key.upper()} for movie: {movie_data.get(key)}")
            if key == "genre":  # Remind user how to input genres before genre input prompt.
                print("\n(Note: Multiple genres must be comma-separated.)")
            new_val = input(f"Enter new {key} or leave blank to keep current: ").strip()
            if new_val:
                # Evaluate different cases to make sure the data is correct.
                if key == "genre":
                    new_val = [genre.strip() for genre in new_val.split(",")]
                elif key == "duration":
                    try:
                        new_val = int(new_val)
                    except (ValueError, TypeError):
                        print("\nPlease enter an integer (e.g. 120).")
                        continue
                elif key == "rating":
                    try:
                        new_val = float(new_val)
                    except (ValueError, TypeError):
                        print("\nPlease enter a float (e.g. 3.4).")
                        continue
                movie_data[key] = new_val
            break
    return movie_data

def _prompt_for_updated_showtime_data(showtime) -> dict:
    print("Updating showtime:")
    showtime_data = showtime.to_dict()
    for key in showtime.editable_attribute_dict_keys:
        while True:
            # Print movies and their IDs for convenience.
            if key == "movie_id":
                print(f"\nMovie IDS:")
                for movie in Movie.current_items.values():
                    print(f"{movie.uid} : {movie.title}")
            # Print current key value for convenience.
            print(f"\nCurrent {key.replace("_", " ").replace("datetime", "date time").upper()} "
                  f"for showing: {showtime_data.get(key)}"
                  f"{bool(key == 'movie_id') * f'({showtime.movie.title})'}")  # ALso print movie if key is movie_id.
            # Ask for new key value.
            new_val = input(f"Enter new {key} or leave blank to keep current: ").strip()
            if new_val:
                if key == "movie_id":
                    if not Movie.current_items.get(new_val, None):
                        print("\nNot a valid ID.")
                        continue
                elif key == "datetime":
                    try:
                        dt.datetime.strptime(new_val, "%Y-%m-%d %H:%M")
                    except (ValueError, TypeError):
                        print("\nPlease format the attribute attribute correctly (YYYY-MM-DD HH:MM).")
                        continue
                elif type(showtime_data[key]) == int:  # For any key where the old value is int
                    try:
                        new_val = int(new_val)
                    except (ValueError, TypeError):
                        print("\nPlease enter an integer.")
                        continue
                showtime_data[key] = new_val
            break
    return showtime_data

def _duplicate_checker(test):
    count = -1
    for item in list(test.current_items.values()):
        if test == item:
            count += 1
    if count > 0:
        return True
    else:
        return False
