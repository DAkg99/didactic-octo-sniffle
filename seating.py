"""
    Tracks & presents seating data.
"""
import os
from threading import Timer

def get_map(occupied_seats: list, seating_dimensions: tuple = (15, 10)) -> list:
    """Generates a seat map for a given list of bookings for a showing"""
    seat_map = [[0 for _ in range(seating_dimensions[0])] for _ in range(seating_dimensions[1])]
    for seat in occupied_seats:
        seat_map[seat[0]][seat[1]] = 1  # Mark seat as filled on map
    return seat_map

def render_map(seats_data: list, terminal_width = 120):  # DEBUG
    """Prints seat map with labels. Splits into parts if window is narrow. Doesn't print if too narrow."""
    if terminal_width < 6:
        print("Your terminal window is too narrow! \nPlease resize it and try again to see available seating.")
        return
    seats_height = len(seats_data)
    seats_width = len(seats_data[0])
    if seats_height > 676:
        raise ValueError("Seat map too large! (Too many rows to enumerate with 2 alphabetic characters)")
    elif seats_width > 98:
        raise ValueError("Seat map too large! (Too many columns to represent with 2 digits (1-indexed))")

    seats_width_effective = (seats_width * 3) + 3  # Expand to fit more information
    fits_screen = bool(seats_width_effective <= terminal_width)

    if fits_screen:  # If it fits, just print it
        print(" " * 3, end="")
        for col in range(len(seats_data)):
            print(f"{col + 1:02d} ", end="")
        print()
        for row in range(len(seats_data[0])):
            _print_row_letters(row)
            for col in range(len(seats_data)):
                if seats_data[col][row] == 1:
                    render_str = "XX "
                else:
                    render_str = "-- "
                print(render_str,end="")
            print()

    if not fits_screen:  # If it doesn't fit, print it in parts while showing labels for each part.
        step_size = (terminal_width // 3)  - 1  # - 1 to make space for label column in each iteration.
        high_cols = step_size
        low_cols = 0
        while high_cols < len(seats_data) + step_size: # Only stop if exceeded max value by a full step.
            if high_cols > len(seats_data):
                high_cols = len(seats_data)  # If exceeded max value, bring it down to max value
            print(" " * 3, end="")
            for col in range(low_cols, high_cols):
                print(f"{col + 1:02d} ", end="")
            print()
            for row in range(len(seats_data[0])):
                _print_row_letters(row)
                for col in range(low_cols, high_cols):
                    if seats_data[col][row] == 1:
                        render_str = "XX "
                    else:
                        render_str = "-- "
                    print(render_str, end="")
                print()
            low_cols = high_cols
            high_cols += step_size



# def render_seat_map(seat_map: dict) -> str: ...
def is_seat_available(seat_map: dict, seat_code: str) -> bool: ...
def reserve_seat(seat_map: dict, seat_code: str) -> dict: ...
def release_seat(seat_map: dict, seat_code: str) -> dict: ...
def select_seats(showing):
    """Make user select seats for a given showing. Selection is validated per showing data."""
    while True:
        seat_map = get_map(showing.occupied_seats, showing.seat_layout)
        render_map(seat_map)
        seats = input("Enter seat or multiple seats (space separated) ('q' to cancel): ").strip().upper().split()
        if not seats or seats[0] == "Q":
            return None
        confirmed_seats = _validate_seats(seats, showing.occupied_seats, showing.seat_layout)
        if not confirmed_seats:
            continue
        reserve_id = showing.temp_reserve_seats_new(confirmed_seats)
        Timer(300, showing.temp_reserve_seats_remove, reserve_id)
        print("Your seats have been reserved for the next 5 minutes.")
        return confirmed_seats


def _validate_seats(seats: list, occupied_seats: list, seat_layout: tuple):
    """Validate given list of seats for a show. Make sure they're already clean (stripped, capitalized, etc.)"""
    final_seats = list()
    seats = list(set(seats))  # Remove duplicates
    for seat in seats:
        if not (len(seat) == 4 and seat[0:2].isalpha() and seat[2:4].isnumeric()):
            print("Error: Invalid seat format. Please try again.\n(E.g.: AB03 AB04 AB05)")
            input("[Enter to continue] ")
            return None
        seat_raw = seat_format2raw(seat)  # Seat format was correct, so we can translate into raw form
        if not ((0 <= seat_raw[0] < seat_layout[0]) and (0 < seat_raw[1] <= seat_layout[1])):
            print("Error: Seats do not exist. Please select a valid seat.")
            input("[Enter to continue] ")
            return None
        if seat_raw in occupied_seats:
            print("Error: One or more of the seats you've selected are no longer available. Please pick again.")
            input("[Enter to continue] ")
            return None
        final_seats.append(seat_raw)
    return final_seats

def seat_format2raw(seat: str) -> tuple:  # Unfinished
    """Translate formatted seat string (AA00) into seat coordinates (C, R)"""
    row = (ord(seat[0]) - 65) * 10 + (ord(seat[1]) - 65) * 1
    return row, int(seat[2:])

def seat_raw2format(seat_raw: list) -> str:
    """Translate seat coordinates [C, R] into formatted string (AA00)"""
    row = seat_raw[0]
    left = row // 26
    right = row % 26
    left = chr(65 + left)
    right = chr(65 + right)
    return (left+right).upper() + str(seat_raw[1])



def _print_row_letters(row):
    left = row // 26
    right = row % 26
    left = chr(65 + left)
    right = chr(65 + right)
    print((left+right).upper()+" ", end="")