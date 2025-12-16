"""
    Creates, cancels, and presents bookings.
"""
import json
from dataclasses import dataclass

@dataclass
class Booking:
    showing_id: str
    name: str
    age: int
    email: str
    seats: list[list]

    @classmethod
    def new(cls, seats_formatted: list[list]):
        seats_raw = seats_formatted



def create_booking(showtimes: list, seat_maps: dict, booking_data: dict) -> dict: ...
def cancel_booking(bookings: list, booking_id: str, seat_maps: dict) -> bool: ...
def calculate_booking_total(seats: list[str], pricing: dict, tax_rate: float, discounts: list[dict]) -> dict: ...
def list_customer_bookings(bookings: list, email: str) -> list: ...
def generate_ticket(booking: dict, directory: str) -> str: ...

def get_specific_bookings(path: str, showing: str) -> list:
    """Get all bookings for a specific showing."""
    all_bookings = json.load(open(path + "bookings.json"))
    bookings = []
    for test_bookings in all_bookings:
        if hash(showing) == test_bookings["hash_id"]:
            bookings.append(test_bookings)
            break
    return bookings