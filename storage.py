import datetime as dt
def user_input_verified_date(prompt_override: str = "") -> dt.datetime | None:
    """Repeatedly prompts user for valid string until it's done (returns datetime) or user cancels (returns None)"""
    # Branchless conditional to determine prompt string, followed by loop to get valid answer from user
    prompt = (f"Enter date (YYYY-MM-DD): " * bool(not prompt_override)  + prompt_override * bool(prompt_override))
    while True:
        try:
            return dt.datetime.strptime(input(prompt), "%Y-%m-%d")
        except ValueError:
            if input("Invalid date. Enter to try again, 'q' to cancel: ").strip().lower() == "q":
                return None
