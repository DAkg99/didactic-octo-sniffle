"""
    Tracks & presents seating data.
"""
import os
from threading import Timer
from dataclasses import dataclass, field

@dataclass
class SeatHandler:
    showing: 'Showing'

    def __post_init__(self):
        self._verify_arrangement()

    def _verify_arrangement(self):
        """Check if seat arrangement is within valid range. Raise error if not."""
        if 1 > self.seat_cols or 1 > self.seat_rows:
            raise ValueError("Seat arrangement must have positive values.")
        if self.seat_rows > 676:
            raise ValueError("Too many seats! (Too many rows to enumerate with 2 alphabetic characters)")
        elif self.seat_cols > 98:
            raise ValueError("Too many seats! (Too many columns to represent with 2 digits (1-indexed))")

    @property
    def seat_map(self):
        """Generates a seat map for a given list of bookings for a showing"""
        seat_map = [[0 for _ in range(self.seat_rows)] for _ in range(self.seat_cols)]
        for seat in self.showing.occupied_seats:
            seat_map[seat[0]][seat[1]] = 1  # Mark seat as filled on map
        return seat_map

    @property
    def seat_cols(self):
        return self.showing.seat_layout[1]
    @property
    def seat_rows(self):
        return self.showing.seat_layout[0]

    def select_seats(self):
        while True:
            self.render_map()
            seats = input("Enter seat or multiple seats (space separated) ('q' to cancel): ").strip().upper().split()
            if not seats or seats[0] == "Q":
                return None
            confirmed_seats = self.clean_validate_selection(seats)
            if not confirmed_seats:
                continue
            reserve_id = self.showing.temp_reserve_seats_new(confirmed_seats)
            Timer(300, self.showing.temp_reserve_seats_remove, reserve_id)
            return confirmed_seats

    def clean_validate_selection(self, seats: list):
        """Validate given list of seats for a show. Make sure they're already clean (stripped, capitalized, etc.)"""
        final_seats = list()
        seats = list(set(seats))  # Remove duplicates
        for seat in seats:
            if not (len(seat) == 4 and seat[0:2].isalpha() and seat[2:4].isnumeric()):
                print("Error: Invalid seat format. Please try again.\n(E.g.: AB03 AB04 AB05)")
                input("[Enter to continue] ")
                return None
            seat_raw = seat_format2raw(seat)  # Seat format was correct, so we can translate into raw form
            if not ((0 <= seat_raw[0] < self.seat_cols) and (0 < seat_raw[1] <= self.seat_rows)):
                print("Error: Seats do not exist. Please select a valid seat.")
                input("[Enter to continue] ")
                return None
            if seat_raw in self.showing.occupied_seats:
                print("Error: One or more of the seats you've selected are no longer available. Please pick again.")
                input("[Enter to continue] ")
                return None
            final_seats.append(seat_raw)
        return final_seats

    def render_map(self):
        """Prints seat map with labels. Splits into parts if window is narrow. Doesn't print if too narrow."""
        # terminal_width = next(iter(os.get_terminal_size()))
        terminal_width = 120  # DEBUG
        chars_per_column = 3
        if terminal_width < 2 * chars_per_column:
            print("Your terminal window is too narrow! \nPlease resize it and try again to see available seating.")
            return
        render_width = ((self.seat_cols + 1) * chars_per_column)  # + 1 For label column.
        fits_screen = bool(render_width <= terminal_width)

        if fits_screen:  # If it fits, just print it
            print(" " * chars_per_column, end="")
            for col in range(1, self.seat_cols + 1):  # Print col labels in the first row
                print(f"{col:02d} ", end="")
            print()
            for row in range(self.seat_rows):
                print(self.col_label(row), end="")  # Print row label at the start of col
                for col in range(self.seat_cols):
                    if self.seat_map[col][row] == 1:
                        render_str = "XX "
                    else:
                        render_str = "-- "
                    print(render_str, end="")
                print()

        if not fits_screen:  # If it doesn't fit, print it in parts while showing labels for each part.
            step_size = (terminal_width // chars_per_column) - 1  # - 1 to make space for label column in each iteration.
            high_cols = step_size
            low_cols = 0
            while high_cols < self.seat_cols + step_size:  # Only stop if exceeded max value by a full step.
                if high_cols > self.seat_cols:
                    high_cols = self.seat_cols  # If exceeded max value, bring it down to max value
                print(" " * chars_per_column, end="")
                for col in range(low_cols + 1, high_cols + 1):
                    print(f"{col:02d} ", end="")
                print()
                for row in range(self.seat_rows):
                    print(self.col_label(row), end="")
                    for col in range(low_cols, high_cols):
                        if self.seat_map[col][row] == 1:
                            render_str = "XX "
                        else:
                            render_str = "-- "
                        print(render_str, end="")
                    print()
                low_cols = high_cols
                high_cols += step_size

    @staticmethod
    def col_label(row):
        return f"{chr(65 + (row // 26))}{chr(65 + (row % 26))} ".upper()


def seat_format2raw(seat: str) -> tuple:  # Unfinished
    """Translate formatted seat string (AA00) into seat coordinates (C, R)"""
    row = (ord(seat[0]) - 65) * 10 + (ord(seat[1]) - 65) * 1
    return row, int(seat[2:])

def seat_raw2format(seat_raw: list) -> str:
    """Translate seat coordinates (C, R) into formatted string (AA00)"""
    row = seat_raw[0]
    left = row // 26
    right = row % 26
    left = chr(65 + left)
    right = chr(65 + right)
    return (left+right).upper() + str(seat_raw[1])

