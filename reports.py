"""Analytic reporting and management"""
import json
import datetime as dt

def revenue_summary(booking_list: list, period: tuple[dt.datetime, dt.datetime]) -> dict:
    data = {
        "range": f"{min(period).strftime("%Y-%m-%d")} - {max(period).strftime("%Y-%m-%d")}",
        "total": 0.0,
        "daily average": 0.0,
        "weekly average": 0.0,
        "monthly average": 0.0,
        "yearly average": 0.0,
    }
    lower_range, higher_range, range_delta = min(period), max(period), abs(period[0] - period[1])
    for booking in booking_list:
        if lower_range <= booking.showtime.datetime <= higher_range:
            data["total"] += booking.cost
    data["daily average"] = round(data["total"] / (range_delta.days + 1), 2)
    data["weekly average"] = round(data["total"] / ((range_delta.days // 7) + 1), 2)
    data["monthly average"] = round(data["total"] / ((range_delta.days // 30) + 1), 2)
    data["yearly average"] = round(data["total"] / ((range_delta.days // 365) + 1), 2)
    return data
