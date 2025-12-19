"""
    Manages movies and their showtimes.
"""

import json
import datetime as dt
from dataclasses import dataclass, field
from typing import ClassVar, Self


@dataclass(frozen=True)
class Movie:
    """Mostly immutable class for movies. Class tracks all current instances in a dict."""
    current_items: ClassVar[dict[str,Self]] = {}  # Dictionary keyed by id
    title: str
    _genre: list[str]
    duration: dt.timedelta
    description: str
    rating: float  # !Mutable! Do not use for hashing.
    uid: str  # Hash in hex form. Set automatically post-init
    _showtimes: list = field(default_factory=list)  # Automatically populated when showtimes are loaded in.

    def __unique_attrs(self):
        return self.title, "".join(self._genre), self.duration, self.description

    def __hash__(self):
        return hash(self.__unique_attrs())

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__unique_attrs() == other.__unique_attrs()
        return False

    def __repr__(self):
        return self.title

    def __post_init__(self):
        if not self.uid:
            object.__setattr__(self, "uid", f"{hash(self)}")
        Movie.current_items[self.uid] = self

    @property
    def genre(self):
        return self._genre
    @property
    def showtimes(self):
        return self._showtimes

    @classmethod
    def from_dict(cls, movie_dict: dict[str, str]):
        """Create instance from dictionary."""
        if not movie_dict.get("uid"):
            movie_dict["uid"] = ""
        return cls(
            movie_dict["title"],
            list(movie_dict["genre"]),
            dt.timedelta(minutes=int((movie_dict["duration"]))),
            movie_dict["description"],
            float(movie_dict["rating"]),
            movie_dict["uid"])

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
        self._showtimes.append(showtime)

    def showtime_rem(self, showtime):
        self._showtimes.remove(showtime)


@dataclass
class Showtime:
    current_items: ClassVar[dict[int, Self]] = {}
    movie: Movie
    datetime: dt.datetime
    screen: int
    attendees: int
    uid: int
    bookings: list = field(default_factory=list)  # Automatically populated when bookings are loaded in.
    __seat_layout: tuple = (15, 10)  # Rows, columns
    __full: bool = False
    __max_attendees: int = 0
    __temporarily_reserved_seats: dict = field(default_factory=dict)

    def __unique_attrs(self):
        return self.movie.uid, self.datetime, self.screen

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__unique_attrs() == other.__unique_attrs()
        return False

    def __repr__(self):
        return (f"Title: {self.movie}\nDate: {self.date}\nTime: {self.time}\nScreen: {self.screen}\n"
                f"Availability: {self.attendees}/{self.__max_attendees}")

    def __post_init__(self):  # Sets up ID, max attendee count, and adds itself to the list of showtimes.
        if not self.uid:
            self.uid = 0
            while True:  # Find the smallest available ID.
                self.uid += 1
                if not self.uid in list(Showtime.current_items.keys()):
                    break
        Showtime.current_items[self.uid] = self
        self.__max_attendees = self.__seat_layout[0] * self.__seat_layout[1]
        self.movie.showtime_add(self)

    def __update_fullness_status(self):
        if self.attendees >= self.__max_attendees:
            self.__full = True
        else:
            self.__full = False


    @property
    def date(self) -> dt.datetime:
        return dt.datetime(self.datetime.year, self.datetime.month, self.datetime.day)
    @property
    def time(self) -> dt.time:
        return dt.time(self.datetime.hour, self.datetime.minute)
    @property
    def seat_layout(self) -> tuple:
        return self.__seat_layout
    @property
    def full(self) -> bool:
        return self.__full
    @property
    def max_attendees(self) -> int:
        return self.__max_attendees
    @property
    def occupied_seats(self) -> list:
        occupied = list(self.__temporarily_reserved_seats.values())
        for booking in self.bookings:
            occupied += booking.seats
        return occupied

    @classmethod
    def from_dict(cls, show_dict: dict):
        return cls(
            Movie.current_items[show_dict["movie"]],
            dt.datetime.strptime(show_dict["datetime"], "%Y-%m-%d %H:%M"),
            show_dict["screen"],
            show_dict["attendees"],
            show_dict.get("uid", 0),
            show_dict.get("bookings", list())
        )

    def to_dict(self):
        return {
            "movie": self.movie.uid,
            "datetime": self.datetime.strftime("%Y-%m-%d %H:%M"),
            "screen": self.screen,
            "attendees": self.attendees,
            "uid": self.uid
        }

    def booking_new(self, booking):
        self.bookings.append(booking)
        self.attendees += len(booking.seats)
        self.__update_fullness_status()

    def booking_remove(self, booking):
        self.bookings.remove(booking)
        self.attendees -= len(booking.seats)
        self.__update_fullness_status()

    def temp_reserve_seats_new(self, seats: list):
        reserve_uid = 0
        while True:  # Find the smallest available ID.
            reserve_uid += 1
            if not reserve_uid in self.__temporarily_reserved_seats.keys():
                break
        self.__temporarily_reserved_seats[reserve_uid] = seats
        return reserve_uid

    def temp_reserve_seats_remove(self, reserve_uid: int):
        if reserve_uid in self.__temporarily_reserved_seats:
            self.__temporarily_reserved_seats.pop(reserve_uid)


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

def add_movie(movies: list, movie_data: dict) -> list:
    """Adds a new movie to the list of movies"""
    movies.append(movie_data)
    return movies

def remove_movie(): # Todo
    pass

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


def list_showtimes(path: str, search_value: str | dt.datetime | None = None) -> list:
    """Lists showtimes, with optional search parameter"""
    showtimes = list(Showtime.current_items.values())
    if not search_value:
        return showtimes
    requested_showtimes = []
    if isinstance(search_value,dt.datetime):
        for item in showtimes:
            if item.date == search_value:
                requested_showtimes.append(item)
    else:
        for item in showtimes:
            if item.movie.title == search_value:
                requested_showtimes.append(item)
    if not requested_showtimes:
        return ["No showings found."]
    return requested_showtimes

def schedule_showtime(showtime_data: dict) -> dict: pass # To-do. Note: Make sure to add showing to bookings.json

def update_showtime(showtimes: list, showtime_id: str, updates: dict) -> dict: ... # To-do.
# Note: Make sure to update bookings.json