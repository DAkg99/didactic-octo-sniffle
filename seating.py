"""
    Tracks & presents seating data.
"""
from threading import Timer

def select_seats(showing) -> list:
    while True:
        if showing.full:
            print("This showing is full.")
            input("[Enter to continue] ")
            return []
        render_map(get_seat_map(showing))
        print("Pick one or multiple space-separated seats.")
        selection = input("Selection ('q' to cancel): ").upper().strip().split()
        if (not selection) or (selection[0] == "Q"):
            return []
        selection[:] = list(set(selection))  # Remove duplicates
        if not is_seat_available(selection, showing):
            input("[Enter to continue] ")  # Wait after error message is printed
        else:
            return selection

def get_seat_map(showing):
    """Generates a seat map for a given list of bookings for a showing"""
    new_map = [[0 for _ in range(showing.seat_rows)] for _ in range(showing.seat_cols)]
    for seat in showing.occupied_seats:
        new_map[seat[1]][seat[0]] = 1  # Mark seat as filled on map
    return new_map

def is_seat_available(seats: list, showing) -> bool:
    """Check if seat input is valid and available"""
    for seat in seats:
        if not (len(seat) == 4 and seat[0:2].isalpha() and seat[2:4].isnumeric()):
            print("Error: Invalid seat format. Please try again.\n(E.g.: AB03 AB04 AB05)")
            return False
        seat_raw = format2raw(seat)
        if not ((0 <= seat_raw[1] < showing.seat_cols) and (0 <= seat_raw[0] < showing.seat_rows)):
            print("Error: Seats do not exist. Please select a valid seat.")
            return False
        if seat_raw in showing.occupied_seats:
            print("Error: One or more of the seats you've selected are no longer available. Please pick again.")
            return False
    return True

def render_map(seating_map):
    """Prints seat map with labels. Splits into parts if window is narrow. Doesn't print if too narrow."""
    # terminal_width = next(iter(os.get_terminal_size()))
    terminal_width = 120  # DEBUG
    char_per_col = 3
    if terminal_width < 2 * char_per_col:
        print("Your terminal window is too narrow! \nWiden it and try again to see available seating.")
        return
    columns, rows = len(seating_map), len(seating_map[1])
    render_width = (columns + 1) * char_per_col  # + 1 For label column.
    fits_screen = bool(render_width <= terminal_width)
    col_labels = lambda _cols, base = 1: f"{' ' * char_per_col}{''.join([f"{i:02d} " for i in range(1, _cols + 1)])}"
    row_label = lambda _row: f"{chr(65 + (_row // 26))}{chr(65 + (_row % 26))} ".upper()

    if fits_screen:
        print(col_labels(columns))
        for row in range(rows):
            print(row_label(row), end="")
            for col in range(columns):
                if seating_map[col][row] == 1:
                    render_str = "XX "
                else:
                    render_str = "-- "
                print(render_str, end="")
            print()

    if not fits_screen:  # If it doesn't fit, print it in parts while showing labels for each part.
        step_size = (terminal_width // char_per_col) - 1  # - 1 to make space for label column in each iteration.
        high_cols = step_size
        low_cols = 0
        while high_cols < columns + step_size:  # Only stop if exceeded max value by a full step.
            if high_cols > columns:
                high_cols = columns  # If exceeded max value, bring it down to max value
            print(col_labels(high_cols, low_cols))
            for row in range(rows):
                print(row_label(row), end="")
                for col in range(low_cols, high_cols):
                    if seating_map[col][row] == 1:
                        render_str = "XX "
                    else:
                        render_str = "-- "
                    print(render_str, end="")
                print()
            low_cols = high_cols
            high_cols += step_size

def reserve_seats_temporary(seats: list, showing, seconds: int = 300):
    """Reserve seats for a showing. Automatically release them after time interval (5 min by default)."""
    reserve_id = showing.reserve_seats_add(seats)
    Timer(seconds, showing.reserve_seats_remove, reserve_id)
    return reserve_id


def format2raw(seat: str) -> tuple:
    """Translate formatted seat string (AA00) into seat coordinates (C, R)"""
    return ((ord(seat[0]) - 65) * 10 + (ord(seat[1]) - 65)), int(seat[2:]) - 1

def raw2format(seat_raw: tuple) -> str:
    """Translate seat coordinates (C, R) into formatted string (AA00)"""
    return f"{chr(65 + seat_raw[0] // 26)}{chr(65 + seat_raw[0] % 26)}{seat_raw[1] + 1:02d}"
