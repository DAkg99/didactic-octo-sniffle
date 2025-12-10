import datetime as dt

def generate_datetime_from_input(input_statement_override: str = "") -> dt.datetime | None:
    """Asks user for YYYY-MM-DD. Returns None is users fails."""
    while True:
        user_string = input((f"Enter date (YYYY-MM-DD): " * bool(not input_statement_override)) +
                  (input_statement_override * bool(input_statement_override))) # Branchless conditional
        try:
            int_data = [int(datum) for datum in user_string.strip().split("-")]
            return dt.datetime(int_data[0], int_data[1], int_data[2])
        except (IndexError, ValueError, TypeError, NameError, OverflowError):
            if input("Invalid date. Press enter to try again, or 'cancel' to go back: ").lower().strip() == "cancel":
                return None
            continue