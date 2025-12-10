import json
import datetime as dt
from dataclasses import dataclass, field


@dataclass
class Movie:
    title: str
    genre: list[str]
    duration: dt.timedelta
    rating: float
    description: str
    showtimes: list[dt.datetime] | None = None

    def __repr__(self):
        return self.title

    @classmethod
    def from_dict(cls, movie_dict: dict[str, str]):
        return cls(
            movie_dict["title"],
            list(movie_dict["genre"]),
            dt.timedelta(minutes=int((movie_dict["duration"]))),
            float(movie_dict["rating"]),
            movie_dict["description"],)


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


def load_showtimes(path: str) -> list:
    """Loads showtime database file"""
    return list(json.load(open(path+"showtimes.json")))

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
        search_type = "date"
    else:
        search_type = "name"
    for item in showtimes:
        if item[search_type] == search_value:
            requested_showtimes.append(item)
    if not requested_showtimes:
        return ["No showings found."]
    return requested_showtimes

def schedule_showtime(showtime_data: dict) -> dict: pass # Todo

def update_showtime(showtimes: list, showtime_id: str, updates: dict) -> dict: ...
