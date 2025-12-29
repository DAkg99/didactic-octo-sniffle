"""Analytic reporting and management"""
import datetime as dt
import json
import os

def occupancy_report(showtimes_list: list) -> dict:
    """Returns analytics in a dictionary."""
    total_max_attendees = 0
    ticket_count = 0
    days = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
        7: "n/a"
    }
    attendees_per_day = [0 for _ in range(7)]
    for showtime in showtimes_list:
        attendees_per_day[showtime.datetime.weekday()] += showtime.attendees
        total_max_attendees += showtime.max_attendees
        ticket_count += len(showtime.bookings)
    data = {
        "total occupancy percent": round(sum(attendees_per_day) / total_max_attendees, 3),
        "average tickets count per showing": round(ticket_count / len(showtimes_list), 3),
        "busiest day(s)": ", ".join([days[index] for index in _busiest_days_indexes(attendees_per_day)])
    }
    return data


def revenue_summary(booking_list: list, showtime_list: list, period: list[dt.datetime] = '') -> dict:
    if not period:  # Determine date range if not given.
        if not showtime_list:
            showtime_list = []
        period = _auto_showtime_date_range(showtime_list)
    data = {
        "range": f"{min(period).strftime("%Y-%m-%d")} - {max(period).strftime("%Y-%m-%d")}",
        "total": 0.0,
        "daily average": 0.0,
        "weekly average": 0.0,
        "monthly average": 0.0,
        "yearly average": 0.0,
    }
    #  Add + 1 days to upper date so both dates entered by user are treated inclusively.
    low_date, high_date = min(period), (max(period) + dt.timedelta(days = 1))
    range_delta = high_date - low_date
    for booking in booking_list:
        if low_date <= booking.showtime.datetime <= high_date:
            data["total"] += booking.cost
    data["daily average"] = round(data["total"] / range_delta.days, 2)
    data["weekly average"] = round(data["total"] / ((range_delta.days // 7) + 1), 2)
    data["monthly average"] = round(data["total"] / ((range_delta.days // 30) + 1), 2)
    data["yearly average"] = round(data["total"] / ((range_delta.days // 365) + 1), 2)
    return data

def top_movies(showtimes_list: list, limit: int = 5) -> list:
    movies_viewer_count = dict()
    for showtime in showtimes_list:
        if not movies_viewer_count.get(showtime.movie):
            movies_viewer_count[showtime.movie] = 0
        movies_viewer_count[showtime.movie] += showtime.attendees
    movies_sorted = [movie for movie, count in sorted(movies_viewer_count.items(), key=lambda item: item[1], reverse=True)]
    return_limit = len(movies_sorted) if len(movies_sorted) <= limit else limit
    return movies_sorted[:return_limit]

def export_report(filename: str, showtimes_list: list, booking_list: list):
    if os.path.exists(filename):
        print("File already exists.")
        return
    export_data = dict()
    export_data["occupancy"] = occupancy_report(showtimes_list)
    export_data["revenue"] = revenue_summary(booking_list, showtimes_list)
    export_data["top_movies"] = [movie.to_dict() for movie in top_movies(showtimes_list)]
    with open(filename+".json", "w") as exp_file:
        json.dump(export_data, exp_file, indent=4)
        print(f"Exported data to {filename}.json")


def _busiest_days_indexes(days_counter: list) -> list:
    """Receives array of 7 elements and returns the indexes of biggest elements. Returns index 7 if they're all zero."""
    max_count = 0
    indexes = []
    for index, count in enumerate(days_counter):
        if count == max_count and max_count != 0:
            indexes.append(index)
        elif count > max_count:
            indexes.clear()
            indexes.append(index)
            max_count = count
    if not indexes:
        indexes = [7]
    return indexes

def _auto_showtime_date_range(showtime_list) -> list:
    dates = [value.datetime for value in showtime_list]
    try:
        date1 = min(dates)
        date2 = max(dates)
    except ValueError:  # When Showtime is empty, default range to today
        date1 = date2 = dt.datetime.now()
    return [date1, date2]