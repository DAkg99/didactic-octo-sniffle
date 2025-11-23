import json

def load_movies(path: str) -> list:
    """Returns movie database as list"""
    return list(json.load(open(path+"movies.json")))

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

def list_showtimes(path: str, request_type: str, search_for = None):
    """Lists showtimes, with optional search"""
    showtimes = load_showtimes(path)
    if request_type == "all":
        return showtimes
    requested_showtimes = []
    for item in showtimes:
        if item[request_type] == search_for:
            requested_showtimes.append(item)
    if not requested_showtimes:
        return ["No showings found."]
    return requested_showtimes
    
def schedule_showtime(showtime_data: dict) -> dict: pass # Todo

def update_showtime(showtimes: list, showtime_id: str, updates: dict) -> dict: ...
