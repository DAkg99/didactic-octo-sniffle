"""
    Manages movies and their showtimes.
"""

import json
import datetime as dt
from dataclasses import dataclass, field
from typing import ClassVar, Self

import storage
from storage import random_uid_generator

@dataclass(frozen=True)
class Movie:
    """Mostly immutable class for movies. Class tracks all current instances in a dict."""
    current_items: ClassVar[dict[str,Self]] = {}                  # CLASS VAR: Automatically self-populates.
    title: str
    genre: list[str]
    duration: dt.timedelta
    description: str
    rating: float = field(compare=False)                          # Mutable (set by update_rating method)
    uid: str = field(compare=False)                               # Mutable (set post init)
    showtimes: list = field(default_factory=list, compare=False)  # Mutable (set by showtime_add/rem methods)

    def __post_init__(self):
        # Generate UID if none provided.
        if not self.uid:
            new_uid = random_uid_generator(self.current_items.keys())
            object.__setattr__(self, "uid", new_uid)
        # Add self to class dictionary.
        Movie.current_items[self.uid] = self

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

    def short_title(self, limit: int = 15):
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

    def update_rating(self, new_rating: str):
        while True:
            try:
                new_rating = float(new_rating)
                break
            except ValueError:
                print("Error: Rating must be between 0 and 5.")
                new_rating = input("Enter new value or (q) to cancel: ").lower().strip()
                if new_rating == "q":
                    return
                continue
        object.__setattr__(self, "rating",new_rating)

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
    temporarily_reserved_seats: dict = field(default_factory=dict)

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

    def pretty_string(self, *, short = False):
        if not short:
            return (f"{f'[{str(self.full).upper()}]' * int(self.full)}"  # [FULL] prefix if full
                f"{self.movie.short_title()} {self.datetime.strftime('%Y %b %d %H:%M')}"
                f"(Screen: {self.screen}, Seats left: {self.max_attendees - self.attendees:03d}/{self.max_attendees} "
                f"Lang: {self.language.title()})")
        else:
            return (f"Showing: {self.movie.title} ({self.datetime.strftime('%Y %b %d %H:%M')} "
                f"Screen {self.screen} (language: {self.language.title()}))")

    @property
    def seat_cols(self) -> int:
        return self.seat_layout[1]
    @property
    def seat_rows(self) -> int:
        return self.seat_layout[0]
    @property
    def occupied_seats(self) -> list:
        occupied = [item for value in self.temporarily_reserved_seats.values() for item in value]
        for booking in self.bookings:
            occupied += booking.seats
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
        self.uid = data_dict.get("uid", 0)

    def booking_new(self, booking):
        self.bookings.append(booking)
        self.__update_attendee_count()
        self.__update_fullness_status()

    def booking_remove(self, booking):
        self.bookings.remove(booking)
        self.__update_attendee_count()
        self.__update_fullness_status()

    def reserve_seats_add(self, seats: list) -> str:
        # Generate unique reservation ID and save reserved seats with ID as the key. Key is returned.
        reserve_uid = storage.random_uid_generator(self.temporarily_reserved_seats.keys())
        self.temporarily_reserved_seats[reserve_uid] = seats
        return reserve_uid

    def reserve_seats_remove(self, reserve_uid: str):
        if reserve_uid in self.temporarily_reserved_seats.keys():
            self.temporarily_reserved_seats.pop(reserve_uid)

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


# Movie functions
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
    new_movie = Movie.from_dict(movie_data)
    if _duplicate_checker(new_movie):
        abort = input("This movie already exists. Abort? (y/n): ").strip().lower()
        if abort != "y":
            remove_movie(new_movie)
            print("New movie creation cancelled.")
            return
    print("New movie created successfully.")
    return

def remove_movie(movie: Movie):
    # Simply delete the movie if there are no showings.
    if not movie.showtimes:
        confirm = True
    else:
        print("WARNING: This movie has associated showtimes, which will be deleted alongside it. "
              "This might affect your analytics.")
        if any([(showing.datetime > dt.datetime.now() and showing.attendees != 0) for showing in movie.showtimes]):
            print("WARNING: This movie has future showtimes which have already been booked. It is NOT recommended to "
                  "retire this movie without refunding the customers first.")
        confirm = (input("Retire movie? (y/n): ").lower().strip() == "y")
    if confirm:
        for showtime in movie.showtimes[::-1]:
            remove_showtime(showtime, True)
        Movie.current_items.pop(movie.uid)
        print("Movie deleted.")
    else:
        print("Movie deletion aborted.")

# Showtime functions
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
    showtime_dict = _prompt_for_showtime_data(movie)
    new_showtime = Showtime.from_dict(showtime_dict)
    if _duplicate_checker(new_showtime):
        abort = input("Identical showtime already exists. Abort? (y/n): ").strip().lower()
        if abort != "y":
            remove_showtime(new_showtime)
            print("New showtime scheduling cancelled.")
            return
    print("New showtime scheduled successfully.")
    return

def remove_showtime(showtime: Showtime, force: bool = False):
    """Remove showtime. Will prompt user for confirmation if bookings exist (unless force is true)."""
    # Simply delete if forced to, or if there are no bookings to worry about.
    if force or (len(showtime.bookings) == 0):
        for booking in showtime.bookings[::-1]:
            booking.delete_self()
        showtime.movie.showtime_rem(showtime)
        Showtime.current_items.pop(showtime.uid)
        del showtime
        return

    # There are bookings; check if this showing has already occurred or not.
    if showtime.datetime > dt.datetime.now():
        print(f"There are active bookings for this showtime. Retiring the showtime will delete these bookings as well.\n"
              f"It is NOT recommended you retire this showtime without refunding the customers first.")
        confirm = (input("Retire showtime? (y/n): ").lower().strip() == "y")
    else:
        print(f"Retiring this showtime will discard its booking data.")
        confirm = (input("Proceed? (y/n): ").lower().strip() == "y")
    if confirm:
        for booking in showtime.bookings:
            booking.delete_self()
        showtime.movie.showtime_rem(showtime)
        Showtime.current_items.pop(showtime.uid)
        del showtime
    else:
        print("Movie deletion aborted.")

def update_showtime(showtime):
    """Prompt user for new data and update showtime accordingly."""
    updated_data = _prompt_for_updated_showtime_data(showtime)
    showtime.update_from_dict(updated_data)
    print(f"Updated showing: \n{showtime}")

def list_showtimes(search_value: str | dt.datetime | None = None) -> list:
    """Lists showtimes, with optional search parameter"""
    showtimes = list(Showtime.current_items.values())
    if not search_value:
        return showtimes
    requested_showtimes = []
    if isinstance(search_value,dt.datetime):
        for item in showtimes:
            if item.datetime.date() == search_value.date():
                requested_showtimes.append(item)
    else:
        for item in showtimes:
            if item.movie.title == search_value:
                requested_showtimes.append(item)
    if not requested_showtimes:
        return ["No showings found."]
    return requested_showtimes


# Helper functions--------
def _prompt_for_movie_data() -> dict:
    new_movie = dict()
    new_movie["title"] = input("Movie title: ").strip().title()
    new_movie["genre"] = input("Enter genre (space-separated if multiple): ").strip().split()
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
            new_showtime["pricing_tier"] = int(input("Enter price tier (usually a number from 1 to 5): "))
            break
        except (ValueError, TypeError, NameError):
            input("Invalid screen (must be an integer).")
    # Get datetime:
    while True:
        try:
            new_showtime["datetime"] = input("Enter date and time (YYYY-MM-DD HH:MM): ")
            dt.datetime.strptime(new_showtime["datetime"] , "%Y-%m-%d %H:%M")
        except (ValueError, TypeError, NameError):
            input("Invalid date/time format.")

def _prompt_for_updated_showtime_data(showtime) -> dict:
    showtime_data = showtime.to_dict()
    for key in showtime.editable_attribute_dict_keys:
        while True:
            print(f"Current {key.replace("_", " ").replace("datetime", "date time").upper()} "
                  f"for showing: {showtime_data.get(key)}")
            new_val = input(f"Enter new {key} or leave blank to keep current: ").strip()
            if new_val:
                if key == "datetime":
                    try:
                        dt.datetime.strptime(new_val, "%Y-%m-%d %H:%M")
                        showtime_data[key] = new_val
                    except (ValueError, TypeError):
                        print("Please format the attribute attribute correctly (YYYY-MM-DD HH:MM).")
                elif type(showtime_data[key]) == int:
                    try:
                        new_val = int(new_val)
                        showtime_data[key] = new_val
                    except (ValueError, TypeError):
                        print("Please enter an integer.")
                else:
                    showtime_data[key] = new_val
                break
            else:
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
