"""
    Tracks & presents seating data.
"""
import os

def initialize_seat_map(existing_bookings: list, seating_dimensions: tuple = (15, 10)) -> list:
    """Generates a seat map for a given list of bookings for a showing"""
    seat_map = [[0 for _ in range(seating_dimensions[0])] for _ in range(seating_dimensions[1])]
    filled_count = 0
    for booking in existing_bookings:  # Fill occupied seats
        for seat in booking["seats"]:  # Note: Seats are 1-indexed
            seat_map[seat[0] - 1][seat[1] - 1] = 1  # Mark seat as filled on map
            filled_count += 1
    if filled_count >= seating_dimensions[0] * seating_dimensions[1]:
        return []  # Showing is full
    return seat_map

def render_seat_map(seats_data: list, terminal_width = 120):  # DEBUG
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
        high_cols = (terminal_width // 3)  - 1 # Each column consists of three chars (including space). -1 for labels.
        low_cols = 0
        while high_cols < len(seats_data) + (terminal_width // 3)  - 1:
            if high_cols > len(seats_data):
                high_cols = len(seats_data)  # Normalise the index if it's too high
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
            high_cols += (terminal_width // 3)  - 1


# def render_seat_map(seat_map: dict) -> str: ...
def is_seat_available(seat_map: dict, seat_code: str) -> bool: ...
def reserve_seat(seat_map: dict, seat_code: str) -> dict: ...
def release_seat(seat_map: dict, seat_code: str) -> dict: ...


def _print_row_letters(row):
    left = row // 26 + 1
    right = row % 26 + 1
    left = chr(96 + left)
    right = chr(96 + right)
    print((left+right).upper()+" ", end="")