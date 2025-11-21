import json

def load_movies(path: str) -> list:
    """Loads movie database file"""
    return list(json.load(open(path+"movies.json")))

def save_movies(path: str, movies: list) -> None:
    """Saves movies to database file"""
    json.dump(movies, open(path+"movies.json","w"))

def add_movie(movies: list, movie_data: dict) -> list:
    """Adds a new movie to the list of movies"""
    movies.append(movie_data)
    return movies
    
def load_showtimes(path: str) -> list:
    """Loads showtime database file"""
    return list(json.load(open(path+"showtimes.json")))


def list_showtimes(path: str, request_type: str, request: str):
    showtimes = load_showtimes(path)
    if request_type == "all":
        return showtimes
    requested_showtimes = []
    for item in showtimes:
        if item[request_type] == request:
            requested_showtimes.append(item)
    if not requested_showtimes:
        return "No showings found."
    else:
        return requested_showtimes
    
def schedule_showtime(showtimes: list, showtime_data: dict) -> dict:
    pass
    
# def list_showtimes(showtimes: list, movie_id: str | None = None, date: str| None = None) -> list: ...
def update_showtime(showtimes: list, showtime_id: str, updates: dict) -> dict: ...
