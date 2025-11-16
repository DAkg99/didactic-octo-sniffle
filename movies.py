import json

def load_movies(path: str) -> list: 
    return json.load(open(path))

def save_movies(path: str, movies: list) -> None:
    json.dump(movies, open(path,"w"))

def add_movie(movies: list, movie_data: dict) -> dict: # Why is output dict??
    ...

def schedule_showtime(showtimes: list, showtime_data: dict) -> dict: ...
def list_showtimes(showtimes: list, movie_id: str | None = None, date: str| None = None) -> list: ...
def update_showtime(showtimes: list, showtime_id: str, updates: dict) -> dict: ...