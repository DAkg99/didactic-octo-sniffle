import main
import bookings
import movies
import seating
import storage
import reports

import datetime as dt
import time

pause_time = 4
storage.load_state(main.data_path)

print("Current showings:")
main.print_list(main.movies.list_showtimes(only_future=True))
time.sleep(pause_time)

showing = list(movies.Showtime.current_items.values())[4]
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

print(f"\n\nGetting a refund for:\n{new_booking.pretty_string()}")
time.sleep(pause_time)

refund_success = bookings.cancel_booking(new_booking.uid, main.booking_refund_policy, force=True)
storage.save_state(main.data_path)
print(f"\nRefund {'un' * bool(not refund_success)}successful.")
time.sleep(pause_time)

print("\nEnd of test script")