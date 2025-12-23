"""
    Creates, cancels, and presents bookings.
"""
import json
from dataclasses import dataclass, field
from typing import ClassVar, Self
import datetime as dt
import movies
import random

@dataclass(frozen=True)
class Booking:
    current_items: ClassVar[dict[str, Self]] = {}
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
        # Initialise UID if absent. Append to parent showtime and class list.
        if not self.uid:
            uid_trial = f"{random.randint(1, 4294967295):08x}"
            while uid_trial in list(Booking.current_items.keys()):
                uid_trial = f"{random.randint(1, 4294967295):08x}"
            object.__setattr__(self, "uid", uid_trial)
        Booking.current_items[self.uid] = self
        self.showtime.booking_new(self)
    def __eq__(self, other):
        return self.__unique_attributes() == other.__unique_attributes()
    def __repr__(self):
        return (f"{self.showtime.short_represent()}\nCustomer: {self.name} ({self.email}) \nSeats: "
                f"{' '.join([f'{chr(65 + seat[0] // 26)}{chr(65 + seat[0] % 26)}{seat[1] + 1:02d}' for seat in self.seats])}")

    @classmethod
    def from_dict(cls, book_dict: dict):
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

    def delete_self(self):
        Booking.current_items.pop(self.uid)
        self.showtime.booking_remove(self)
        del self


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
    # Set up booking data
    booking_dict = dict()
    booking_dict["showtime_id"] = showtime.uid
    booking_dict["seats"] = ", ".join([f"{seat[0]}-{seat[1]}" for seat in seats])
    booking_dict["name"], booking_dict["age"], booking_dict["email"] = _ask_user_info()
    booking_dict["issued"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    booking_dict["cost"] = calc_total(pricing_data, booking_dict)
    return booking_dict

def cancel_booking(booking_id: str, policy: dict) -> bool:
    booking = Booking.current_items.get(booking_id, None)
    if not booking:
        print("Invalid booking ID.")
        return False
    hours_since_purchase = _timedelta_to_hours(dt.datetime.now() - booking.issued)
    hours_til_showtime = _timedelta_to_hours(booking.showtime.datetime - dt.datetime.now())
    # Check cases.
    if input(f"{booking}\nIs the above booking the one you wish to cancel? (y/n)").lower().strip() == "n":
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
    booking.delete_self()
    print(f"{booking.cost}₺ has been refunded to your account.")
    return True

def calc_total(pricing: dict, booking_data: dict) -> int:
    seat_count = len(booking_data["seats"].split(", "))
    discount_data = pricing["discounts"]
    base_price = pricing["pricing_tiers"][movies.Showtime.current_items[booking_data["showtime_id"]].pricing_tier]
    price = seat_count * base_price * (100 + pricing["tax"]) / 100
    # Apply group discount
    if seat_count >= discount_data["group"][0]:
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

def payment(cost: float, showtime, seats_formatted: list[str], reserve_id) -> bool:
    """Make payment and release reserved seats."""
    print(f"Movie {showtime.movie.title} at {showtime.date.strftime('%Y %b %d')} {showtime.time.strftime('%H:%M')}:\n"
          f"Seats: {', '.join(seats_formatted)}")
    print(f"Your total is {cost}₺")
    if input("Enter payment details ('q' to cancel): ").lower().strip() == "q":
        print("Payment cancelled.")
        success = False
    else:
        print("Payment successful.")
        success = True
    showtime.reserve_seats_remove(reserve_id)
    return success

def list_customer_bookings(email: str) -> list:
    booking_list = []
    for booking in list(Booking.current_items.values()):
        if booking.email == email:
            booking_list.append(booking)
    return booking_list

def generate_ticket(booking_data: dict, path: str):
    booking_id = Booking.from_dict(booking_data).save_to_database(path)
    print(f"Booking made successfully.\n"
          f"{'-' * 10} SAVE YOUR BOOKING ID {'-' * 10}\n"
          f"Booking ID: {booking_id}\n"
          f"{'-' * 10} SAVE YOUR BOOKING ID {'-' * 10}")

def _timedelta_to_hours(delta: dt.timedelta) -> float:
    return (((delta.days * 24) +
            (delta.seconds / (60 * 60))) +
            (delta.microseconds / (1000000 * 60 * 60)))


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
