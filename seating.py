"""
    Tracks & presents seating data.
"""
import datetime as dt

def select_seats(showing) -> list | None:
    """Print map and select seats, return seats as (formatted, raw) tuple along with temp reservation ID."""
    while True:
        if showing.full:
            print("This showing is full.")
            input("[Enter to continue] ")
            return None
        render_map(get_seat_map(showing))
        print("Select one or multiple (space-separated) seats.")
        formatted_seats = input("Selection ('q' to cancel): ").upper().strip().split()
        if (not formatted_seats) or (formatted_seats[0] == "Q"):
            print("Seat selection cancelled.")
            return None
        formatted_seats[:] = list(set(formatted_seats))  # Remove duplicates
        if not is_seat_available(formatted_seats, showing):
            return None  # Invalid seat
        else:
            return [format2raw(seat) for seat in formatted_seats]

def get_seat_map(showing):
    """Generates a seat map for a given list of bookings for a showing"""
    new_map = [[0 for _ in range(showing.seat_rows)] for _ in range(showing.seat_cols)]
    for reserved_seat in showing.occupied_seats["reserved"]:
        new_map[reserved_seat[1]][reserved_seat[0]] = 2  # Mark reserved seats
    for purchased_seat in showing.occupied_seats["confirmed"]:
        new_map[purchased_seat[1]][purchased_seat[0]] = 1  # Mark purchased seats
    return new_map

def is_seat_available(seats: list, showing, user_reservation = None) -> bool:
    """Check if seat input is valid and available"""
    for seat in seats:
        if not (len(seat) == 4 and seat[0:2].isalpha() and seat[2:4].isnumeric()):
            print("Error: Invalid seat format.\n(Valid formatting examples: AB03 AB04 AB05)")
            return False
        seat_raw = format2raw(seat)
        if not ((0 <= seat_raw[1] < showing.seat_cols) and (0 <= seat_raw[0] < showing.seat_rows)):
            print("Error: Seats do not exist.")
            return False
        if seat_raw in [seat for seats_list in showing.occupied_seats.values() for seat in seats_list]:
            if user_reservation and (seat_raw in user_reservation.seats):
                pass  # Skip if seat is 'occupied' by user's own reservation.
            else:
                print("Error: One or more of the seats you've selected are no longer available.")
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
    colum_count, row_count = len(seating_map), len(seating_map[1])
    render_width = (colum_count + 1) * char_per_col  # + 1 For label column.
    fits_screen = bool(render_width <= terminal_width)

    if fits_screen:
        _do_print(seating_map, row_count, colum_count, chr_per_col= char_per_col)
    else:
        col_step_size = (terminal_width // char_per_col) - 1  # - 1 to make space for label column in each iteration.
        col_max = col_step_size
        col_min = 0
        while col_max < colum_count + col_step_size:  # Only stop if exceeded max value by a full step.
            if col_max > colum_count:
                col_max = colum_count  # If exceeds max value (but not by a full step), bring it down to max value
            _do_print(seating_map, row_count, col_max, col_min, char_per_col)
            col_min = col_max
            col_max += col_step_size

def reserve_seats(seats: list[tuple], showing, booking_cls, reserve_id = '') -> tuple[str, 'Booking']:
    """Make a dummy booking for reserved seats. Supply reserve_id if you want to 'refresh' a reservation."""
    reserve = booking_cls(
            showtime = showing,
            name = "",
            age = 0,
            email = "",
            issued = dt.datetime.now(),
            cost = 0,
            seats = seats,
            confirmed = False,
            uid = reserve_id
        )
    reserve_id = reserve.uid
    return reserve_id, reserve


def format2raw(seat: str) -> tuple:
    """Translate formatted seat string (AA00) into seat coordinates (C, R)"""
    return ((ord(seat[0]) - 65) * 10 + (ord(seat[1]) - 65)), int(seat[2:]) - 1

def raw2format(seat_raw: tuple) -> str:
    """Translate seat coordinates (C, R) into formatted string (AA00)"""
    return f"{chr(65 + seat_raw[0] // 26)}{chr(65 + seat_raw[0] % 26)}{seat_raw[1] + 1:02d}"

def _do_print(seating_map: dict, rows: int, col_max: int, col_min: int = 0, chr_per_col = 3, chr_per_seat = 2):
    """Helper function which prints the seat map."""
    if chr_per_col < chr_per_seat:
        raise ValueError("Seats (being represented within columns) cannot have more chars than the column.")
    # Create the strings which will represent seats.
    occupied_str = ("X" * chr_per_seat) + ((chr_per_col - chr_per_seat) * " ")
    reserved_str = ("R" * chr_per_seat) + ((chr_per_col - chr_per_seat) * " ")
    available_str = ("-" * chr_per_seat) + ((chr_per_col - chr_per_seat) * " ")
    # Esoteric functions which create the label strings.
    col_labels = lambda _col_max, _col_min: f"{' ' * chr_per_col}{''.join([f"{i:02d} " for i in range(_col_min + 1, _col_max + 1)])}"
    row_label = lambda _row: f"{chr(65 + (_row // 26))}{chr(65 + (_row % 26))} ".upper()
    # Render the map.
    print(col_labels(col_max, col_min))  # Column labels (01, 02, ...) (printed at once in one row)
    for row in range(rows):
        print(row_label(row), end="")  # Row labels (AA, AB, ...) (separate for each row)
        for col in range(col_min, col_max):
            # Fill in the seats
            if seating_map[col][row] == 1:
                render_str = occupied_str
            elif seating_map[col][row] == 2:
                render_str = reserved_str
            else:
                render_str = available_str
            print(render_str, end="")
        print()