"""
    Manages movies and their showtimes.
"""

import json
import datetime as dt
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class Movie:
    """Immutable movie object. Rating ARE mutable (use method). Class keeps dictionary of all instances."""
    current_items: ClassVar[dict] = dict()
    title: str
    genre: list[str]
    duration: dt.timedelta
    rating: float  # !Mutable! Do not use for hashing.
    description: str

    def __unique_attrs(self):
        return self.title, "".join(self.genre), self.duration, self.description

    def __hash__(self):
        return hash(self.__unique_attrs())

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__unique_attrs() == other.__unique_attrs()
        return False

    def __repr__(self):
        return self.title

    def __post_init__(self):
        while True:
            if not Movie.current_items.get(self):
                Movie.current_items[self] = self
            elif Movie.current_items.get(self) == self:
                break # Movie already in database, ignore.

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

    @classmethod
    def from_dict(cls, movie_dict: dict[str, str]):
        return cls(
            movie_dict["title"],
            list(movie_dict["genre"]),
            dt.timedelta(minutes=int((movie_dict["duration"]))),
            float(movie_dict["rating"]),
            movie_dict["description"],)

@dataclass
class Showtime:
    title: str
    datetime: dt.datetime

    def date(self) -> dt.datetime:
        return dt.datetime(self.datetime.year, self.datetime.month, self.datetime.day)
    def time(self) -> dt.time:
        return dt.time(self.datetime.hour, self.datetime.minute)

    def date_str(self) -> str:
        return self.datetime.strftime("%Y-%m-%d")
    def time_str(self) -> str:
        return self.datetime.strftime("%H:%M")

    def __repr__(self):
        return f"Title: {self.title}\t\tDate: {self.date()}\t\tTime: {self.time()}"

    @classmethod
    def from_dict(cls, show_dict: dict[str, str]):
        return cls(
            show_dict["title"],
            dt.datetime.strptime(f"{show_dict['time']} {show_dict['date']}","%H:%M %Y-%m-%d"))


def load_movies(path: str) -> list[Movie]:
    """Returns movie database as list"""
    movies_raw_list = json.load(open(path+"movies.json"))
    movies_list = []
    for item in movies_raw_list:
        movies_list.append(Movie.from_dict(item))
    return movies_list

def save_movies(path: str, movies: list) -> None:
    """Saves movies to database file"""
    json.dump(movies, open(path+"movies.json","w"))

def add_movie(movies: list, movie_data: dict) -> list:
    """Adds a new movie to the list of movies"""
    movies.append(movie_data)
    return movies

def remove_movie(): # Todo
    pass


# def load_showtimes(path: str) -> list:
#     """Loads showtime database file"""
#     return list(json.load(open(path+"showtimes.json")))

def load_showtimes(path: str) -> list[Showtime]:
    """Loads showtime database file"""
    showtimes_raw_list = json.load(open(path + "showtimes.json"))
    showtimes_list = []
    for item in showtimes_raw_list:
        showtimes_list.append(Showtime.from_dict(item))
    return showtimes_list

def save_showtimes(path: str, showtimes: list) -> None:
    """Saves showtimes to database file"""
    json.dump(showtimes, open(path+"showtimes.json","w"))

def list_showtimes(path: str, search_value: str | dt.datetime | None = None) -> list:
    """Lists showtimes, with optional search"""
    showtimes = load_showtimes(path)
    if not search_value:
        return showtimes
    requested_showtimes = []
    if isinstance(search_value,dt.datetime):
        for item in showtimes:
            if item.date() == search_value:
                requested_showtimes.append(item)
    else:
        for item in showtimes:
            if item.title == search_value:
                requested_showtimes.append(item)
    if not requested_showtimes:
        return ["No showings found."]
    return requested_showtimes

def schedule_showtime(showtime_data: dict) -> dict: pass # Todo

def update_showtime(showtimes: list, showtime_id: str, updates: dict) -> dict: ...
