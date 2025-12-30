import main
import bookings
import movies
import seating
import storage
import reports

import datetime as dt
import tempfile
import json
import time
import os

# Pause time (seconds) between each step
pause_time = 4

# Data for testing
test_movie_data = [
    {
        "title": "A Clockwork Lemon",
        "genre": ["slice of life", "coming of age", "family"],
        "duration": 113,
        "description": "Well-behaved group of youth seek opportunities to contribute to their local community",
        "rating": 3.21,
        "uid": "abc123d4"
    },
    {
        "title": "A Loud Place",
        "genre": ["horror", "thriller"],
        "duration": 132,
        "description": "Family must constantly scream if they don't want to die to creatures who hunt quiet people.",
        "rating": 1.32,
        "uid": "bcd234e5"
    },
    {
        "title": "Amele",
        "genre": ["slice of life", "comedy"],
        "duration": 129,
        "description": "Odd French girl learns how to become a blue collar worker in Turkey.",
        "rating": 4.23,
        "uid": "cde345f6"
    }
]

test_showtime_data = [
    {
        "movie_id": test_movie_data[0]["uid"],
        "datetime": "2030-06-15 14:30",
        "screen": 4,
        "language": "english",
        "pricing_tier": 4,
        "uid": 1
    },
    {
        "movie_id": test_movie_data[1]["uid"],
        "datetime": "2030-07-16 15:40",
        "screen": 1,
        "language": "turkish",
        "pricing_tier": 2,
        "uid": 2
    },
    {
        "movie_id": test_movie_data[1]["uid"],
        "datetime": "2030-07-16 16:40",
        "screen": 2,
        "language": "english",
        "pricing_tier": 1,
        "uid": 3
    },
    {
        "movie_id": test_movie_data[2]["uid"],
        "datetime": "2030-07-17 12:30",
        "screen": 1,
        "language": "french",
        "pricing_tier": 1,
        "uid": 4
    }
]

test_booking_data = [
    {
    "showtime_id": test_showtime_data[0]["uid"],
    "name": "Smart Fella",
    "age": 30,
    "email": "smart@fella.org",
    "issued": "2025-01-01 01:01:01.000004",
    "cost": 9999,
    "seats": "4-7, 4-8",
    "confirmed": True,
    "uid": "xyz123i4"
    },
    {
    "showtime_id": test_showtime_data[1]["uid"],
    "name": "Test User",
    "age": 30,
    "email": "test@user.net",
    "issued": "2025-01-01 01:01:01.000004",
    "cost": 9999,
    "seats": "5-3",
    "confirmed": True,
    "uid": "yzi234j5"
    }
]

# Where testing happens----------------------------------------

print("Creating test files/folders/data.")
temp_path = tempfile.TemporaryDirectory()
main.data_path = temp_path.name
with open(main.data_path + "movies.json", "w") as mjn:
    json.dump(test_movie_data, mjn, indent=4)
with open(main.data_path + "showtimes.json", "w") as sjn:
    json.dump(test_showtime_data, sjn, indent=4)
with open(main.data_path + "bookings.json", "w") as bjn:
    json.dump(test_booking_data, bjn, indent=4)
storage.load_state(main.data_path)
print("Success")
time.sleep(pause_time/2)

print("\nCurrent showings:")
main.print_list(main.movies.list_showtimes(only_future=True))
time.sleep(pause_time)

showing = list(movies.Showtime.current_items.values())[0]
print(f"\nBooking a ticket for: \n{showing.pretty_string()}")
time.sleep(pause_time)

seating.render_map(seating.get_seat_map(showing))
seats_str = "AB03 AB04"
print("\nSelecting seats: AB03 AB04")
time.sleep(pause_time)

print("Are seats available?")
if seating.is_seat_available(seats_str.split(), showing):
    print("Yes. Proceeding.")
    booking_dict = dict()
    booking_dict["showtime_id"] = showing.uid
    booking_dict["seats"] = "1-2, 1-3"
    booking_dict["name"] = "Test Script Dummy User"
    booking_dict["age"] = 90
    booking_dict["email"] = "test@script.dummy"
    booking_dict["issued"] = dt.datetime.now().isoformat()
    booking_dict["cost"] = bookings.calc_total(main.pricing_data, booking_dict)
    booking_dict["confirmed"] = True
    new_booking = bookings.Booking.from_dict(booking_dict)
    print(f"\nSuccessfully booked. Booking number: {new_booking.uid}")
    storage.save_state(main.data_path)
else:
    print("No. Aborting script...")
    quit()
time.sleep(pause_time)

seating.render_map(seating.get_seat_map(showing))
print(f"\nNew seating map ^")
time.sleep(pause_time)

main.print_list(reports.top_movies(list(movies.Showtime.current_items.values()), limit=3), double_spaced=True)
print(f"\nThese ^ are the top three movies for the theater.")
time.sleep(pause_time)

print(f"\n\nGetting a refund for:\n{new_booking.pretty_string()}\n")
time.sleep(pause_time)

refund_success = bookings.cancel_booking(new_booking.uid, main.booking_refund_policy, force=True)
storage.save_state(main.data_path)
print(f"\nRefund {'un' * bool(not refund_success)}successful.")
time.sleep(pause_time)

print("\nDeleting test data...")
temp_path.cleanup()
print("\nEnd of test script.")