"""
    Creates, cancels, and presents bookings.
"""
import json
from dataclasses import dataclass, field
import movies

@dataclass
class Booking:
    showtime: movies.Showtime
    name: str
    age: int
    email: str
    seats: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, book_dict: dict):
        return cls(
            movies.Showtime.current_items[book_dict["showtime_id"]],
            book_dict["name"],
            book_dict["age"],
            book_dict["email"],
            book_dict["seats"].split(", ")
        )

    def to_dict(self):
        return {
            "showtime_id": self.showtime.uid,
            "name": self.name,
            "age": self.age,
            "email": self.email,
            "seats": ", ".join(self.seats)
        }


# def create_booking(showtimes: list, seat_maps: dict, booking_data: dict) -> dict: ...
# def cancel_booking(bookings: list, booking_id: str, seat_maps: dict) -> bool: ...
def calculate_booking_total(pricing: dict, booking_data: dict) -> int:
    discount_data = pricing["discounts"]
    price = (len(booking_data["seats"]) * pricing["price"]) * pricing["tax"]
    # Apply group discount
    if len(booking_data["seats"]) >= discount_data["group"][0]:
        price *= (discount_data["group"][1] / 100)
    # Apply age discounts
    if booking_data["age"] <= discount_data["min_age"][0]:
        price *= (discount_data["min_age"][1] / 100)
    elif booking_data["age"] >= discount_data["min_age"][0]:
        price *= (discount_data["max_age"][1] / 100)
    # Apply student discount
    if discount_data["student"][0] in booking_data["email"]:
        price *= (discount_data["student"][1] / 100)
    return price

def list_customer_bookings(bookings: list, email: str) -> list: ...
def generate_ticket(booking: dict, directory: str) -> str: ...


def get_specific_bookings(path: str, showing) -> list:
    """Get all bookings for a specific showing."""
    all_bookings = json.load(open(path + "bookings.json"))
    bookings = []
    for test_bookings in all_bookings:
        if hash(showing) == test_bookings["hash_id"]:
            bookings.append(test_bookings)
            break
    return bookings

def save_booking(path, booking):
    """Saves showtimes to database file"""
    json.dump(
        booking.to_dict(),
        open(path + "bookings.json", "a"), indent=4
    )