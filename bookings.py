"""
    Creates, cancels, and presents bookings.
"""
import json
from dataclasses import dataclass, field
from typing import ClassVar
import datetime as dt
import movies
import random

@dataclass(frozen=True)
class Booking:
    ids: ClassVar[set] = set()
    showtime: movies.Showtime
    name: str
    age: int
    email: str
    issued: dt.datetime
    cost: float
    seats: list[tuple] = field(default_factory=list)
    uid: str = ''  # Set during __post_init__

    def __unique_attributes(self):
        return self.showtime.uid, self.name, self.age, self.email, "".join([str(seat) for seat in self.seats]), self.cost
    def __hash(self):
        print(hash(self.__unique_attributes()))
        return hash(self.__unique_attributes())
    def __post_init__(self):
        self.showtime.booking_new(self)  # Append to associated showtime
        if not self.uid:  # Get UID
            while True:
                uid_trial = f"{random.randint(1, 4294967295):08x}"
                if uid_trial not in Booking.ids:
                    break
            Booking.ids.add(uid_trial)
            object.__setattr__(self, "uid", uid_trial)
    def __eq__(self, other):
        return self.__unique_attributes() == other.__unique_attributes()

    @classmethod
    def from_dict(cls, book_dict: dict, price = None):
        if not book_dict.get("cost"):
            if not price:
                raise TypeError("Cost attribute missing!")
            else:
                book_dict["cost"] = price
        return cls(
            movies.Showtime.current_items[book_dict["showtime_id"]],
            book_dict["name"],
            book_dict["age"],
            book_dict["email"],
            dt.datetime.strptime(book_dict["issued"], "%Y-%m-%d %H:%M"),
            book_dict["cost"],
            [tuple([int(value) for value in seat.split("-")]) for seat in book_dict["seats"].split(", ")],
            book_dict.get("uid")
        )

    def to_dict(self):
        return {
            "showtime_id": self.showtime.uid,
            "name": self.name,
            "age": self.age,
            "email": self.email,
            "issued": self.issued.strftime("%Y-%m-%d %H:%M"),
            "cost": self.cost,
            "seats": ", ".join([f"{seat[0]}-{seat[1]}" for seat in self.seats]),
            "uid": self.uid
        }

    def save_to_database(self, path) -> str:
        with open(path + "bookings.json", "r") as book_f:
            all_bookings = json.load(book_f)
        with open(path + "bookings.json", "w") as book_f:
            all_bookings.append(self.to_dict())
            json.dump(all_bookings, book_f, indent=4)
        return self.uid

def load_bookings(path):
    """Loads bookings. Probably a bad idea to keep them all in memory."""
    bookings_data = json.load(open(path+"bookings.json"))
    [Booking.from_dict(booking_data) for booking_data in bookings_data]


def new_booking(showtime, seats: list[tuple]) -> dict | None:
    booking_dict = dict()
    booking_dict["showtime_id"] = showtime.uid
    booking_dict["seats"] = ", ".join([f"{seat[0]}-{seat[1]}" for seat in seats])
    booking_dict["name"], booking_dict["age"], booking_dict["email"] = _ask_user_info()
    booking_dict["issued"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    return booking_dict

# def cancel_booking(bookings: list, booking_id: str, seat_maps: dict) -> bool: ...

def calc_total(pricing: dict, booking_data: dict) -> int:
    discount_data = pricing["discounts"]
    price = (len(booking_data["seats"]) * pricing["price"]) * pricing["tax"]
    # Apply group discount
    if len(booking_data["seats"]) >= discount_data["group"][0]:
        price *= (100 - discount_data["group"][1]) / 100
    # Apply age discounts
    if booking_data["age"] <= discount_data["min_age"][0]:
        price *= (100 - discount_data["min_age"][1]) / 100
    elif booking_data["age"] >= discount_data["min_age"][0]:
        price *= (100 - discount_data["max_age"][1]) / 100
    # Apply student discount
    if discount_data["student"][0] in booking_data["email"]:
        price *= (100 - discount_data["student"][1]) / 100
    return price


def list_customer_bookings(bookings: list, email: str) -> list: ...
def generate_ticket(booking: dict, directory: str) -> str: ...

def get_specific_bookings(path: str, showing) -> list:
    """Get all bookings for a specific showing."""
    with (open(path + "bookings.json")) as book_f:
        all_bookings = json.load(book_f)
    bookings = []
    for test_bookings in all_bookings:
        if hash(showing) == test_bookings["hash_id"]:
            bookings.append(test_bookings)
            break
    return bookings

def _ask_user_info() -> tuple[str, int, str]:
    while True: # Get name
        name = (input("Enter your full name: "))
        if not name:
            print("Name can't be blank")
            continue
        break
    while True: # Get age
        try:
            age = (int(input("Enter your age: ")))
            break
        except (TypeError, ValueError):
            print("Please enter an integer.")
    while True: # Get email
        email = input("Enter your email address: ").strip().lower()
        if email.find("@") == -1:
            print("Please enter a valid email address.")
            continue
        elif email[email.find("@"):].find(".") == -1:
            print("Please enter a valid email address.")
        else:
            break
    return name, age, email
