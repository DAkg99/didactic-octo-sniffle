"""
    Creates, cancels, and presents bookings.
"""
import json
from dataclasses import dataclass, field
from typing import ClassVar, Self
import datetime as dt
import movies

from storage import random_uid_generator


@dataclass(frozen=True)
class Booking:
    max_reserve_mins: ClassVar[float] = 5
    current_items: ClassVar[dict[str, Self]] = {}
    showtime: movies.Showtime
    name: str
    age: int
    email: str
    issued: dt.datetime
    cost: float
    seats: list[tuple]
    confirmed: bool
    uid: str = field(default='', compare=False)  # Mutable (set post init)

    def __post_init__(self):
        # Generate UID if none provided.
        if not self.uid:
            new_uid = random_uid_generator(self.current_items.keys())
            object.__setattr__(self, "uid", new_uid)
        # Add self to class dictionary & parent Showtime.
        Booking.current_items[self.uid] = self
        self.showtime.booking_new(self)

    @property
    def minutes_since_issued(self):
        return (dt.datetime.now() - self.issued) / dt.timedelta(minutes=1)

    @classmethod
    def from_dict(cls, book_dict: dict):
        return cls(
            movies.Showtime.current_items[book_dict["showtime_id"]],
            book_dict["name"],
            book_dict["age"],
            book_dict["email"],
            dt.datetime.fromisoformat(book_dict["issued"]),
            book_dict["cost"],
            [tuple([int(value) for value in seat.split("-")]) for seat in book_dict["seats"].split(", ")],
            book_dict["confirmed"],
            book_dict.get("uid", '')
        )

    def to_dict(self):
        return {
            "showtime_id": self.showtime.uid,
            "name": self.name,
            "age": self.age,
            "email": self.email,
            "issued": str(self.issued),
            "cost": self.cost,
            "seats": ", ".join([f"{seat[0]}-{seat[1]}" for seat in self.seats]),
            "confirmed": self.confirmed,
            "uid": self.uid
        }

    def remove_self(self):
        Booking.current_items.pop(self.uid)
        self.showtime.booking_remove(self)

    def pretty_string(self):
        return (f"{self.showtime.pretty_string(short=True)}\n"
                f"Customer: {self.name} ({self.email})\n"
                f"Seats: "
         f"{' '.join([f'{chr(65 + seat[0] // 26)}{chr(65 + seat[0] % 26)}{seat[1] + 1:02d}' for seat in self.seats])}")


def load_bookings(path):
    bookings_raw_list = json.load(open(path+"bookings.json"))
    for item in bookings_raw_list:
        Booking.from_dict(item)
    return list(Booking.current_items.values())

def save_bookings(path):
    """Saves showtimes to database file"""
    with open(path+"bookings.json", "w") as bookings_f:
        json.dump([booking.to_dict() for booking in Booking.current_items.values()], bookings_f, indent=4)

def new_booking(showtime, seats: list[tuple], pricing_data: dict) -> dict:
    """Generates booking data as a dictionary."""
    booking_dict = dict()
    booking_dict["showtime_id"] = showtime.uid
    booking_dict["seats"] = ", ".join([f"{seat[0]}-{seat[1]}" for seat in seats])
    booking_dict["name"], booking_dict["age"], booking_dict["email"] = _ask_user_info()
    booking_dict["issued"] = dt.datetime.now().isoformat()
    booking_dict["cost"] = calc_total(pricing_data, booking_dict)
    booking_dict["confirmed"] = True
    return booking_dict

def cancel_booking(booking_id: str, policy: dict, force: bool = False) -> bool:
    """Cancels booking of given ID"""
    # Verify that booking with such ID exists.
    booking = Booking.current_items.get(booking_id, None)
    if not booking:
        print("Invalid booking ID.")
        return False
    # See if customer can get a refund.
    hours_since_purchase = (dt.datetime.now() - booking.issued) / dt.timedelta(hours=1)
    hours_til_showtime = (booking.showtime.datetime - dt.datetime.now()) /  dt.timedelta(hours=1)
    if force:
        pass  # Don't prompt user to make sure they're cancelling the wrong ticket.
    else:
        if input(f"{booking.pretty_string()}\nIs the above booking the one you wish to cancel? (y/n)").lower().strip() == "n":
            print("Please enter a different booking ID.")
            return False
    if hours_since_purchase > policy["purchase_time_limit_hours"]:
        print(f"No refund available: {policy['purchase_time_limit_hours']} hours have passed since purchase.")
        return False
    if hours_til_showtime < 0:
        print(f"No refund available: Showing has already begun.")
        return False
    elif hours_til_showtime < policy["film_proximity_limit_hours"]:
        print(f"No refund available: You can't get a refund for a movie which is "
              f"about to begin in {policy['purchase_time_limit_hours']} hours")
        return False
    # Grant refund.
    print(f"{booking.cost:.02f}₺ has been refunded to your account.")
    booking.remove_self()
    del booking
    return True

def calc_total(pricing: dict, booking_data: dict) -> int:
    """Calculate the cost of a given ticket."""
    booking_seat_count = len(booking_data["seats"].split(", "))
    discount_data = pricing["discounts"]
    per_seat_cost = pricing["pricing_tiers"][movies.Showtime.current_items[booking_data["showtime_id"]].pricing_tier]
    price = booking_seat_count * per_seat_cost * (100 + pricing["tax"]) / 100  # Get base price with tax
    if booking_seat_count >= discount_data["group"][0]:  # Apply group discount
        price *= (100 - discount_data["group"][1]) / 100
    if booking_data["age"] <= discount_data["min_age"][0]:  # Apply age discounts
        price *= (100 - discount_data["min_age"][1]) / 100
    elif booking_data["age"] >= discount_data["min_age"][0]:
        price *= (100 - discount_data["max_age"][1]) / 100
    if discount_data["student"][0] in booking_data["email"]:  # Apply student discount
        price *= (100 - discount_data["student"][1]) / 100
    return price

def payment(booking_data: dict) -> bool:
    """Make payment and release reserved seats."""
    print(f"Your total is {booking_data['cost']:.02f}₺")
    if input("Enter payment details ('q' to cancel): ").lower().strip() == "q":
        return False
    return True

def list_customer_bookings(email: str) -> list:
    booking_list = []
    for booking in list(Booking.current_items.values()):
        if booking.email == email:
            booking_list.append(booking)
    return booking_list

def generate_ticket(booking_data: dict):
    booking_id = Booking.from_dict(booking_data).uid
    print(f"Booking made successfully.\n"
          f"{'-' * 10} SAVE YOUR BOOKING ID {'-' * 10}\n"
          f"Booking ID: {booking_id}\n"
          f"{'-' * 10} SAVE YOUR BOOKING ID {'-' * 10}")

def _ask_user_info() -> tuple[str, int, str]:
    # Get name
    while True:
        name = (input("Enter your full name: ")).strip().title()
        if not name:
            print("Name can't be blank")
            continue
        break
    # Get age
    while True:
        try:
            age = (int(input("Enter your age: ")))
            break
        except (TypeError, ValueError):
            print("Please enter an integer.")
    # Get email
    while True:
        email = input("Enter your email address: ").strip().lower()
        if email.find("@") == -1:
            print("Please enter a valid email address.")
            continue
        elif email[email.find("@"):].find(".") == -1:
            print("Please enter a valid email address.")
        else:
            break
    return name, age, email
