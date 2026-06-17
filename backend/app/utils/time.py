from datetime import datetime


def calculate_hours(start_time: str | None, end_time: str | None, fallback: float = 0) -> float:
    if not start_time or not end_time:
        return fallback or 0
    try:
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        hours = (end - start).total_seconds() / 3600
        if hours < 0:
            hours += 24
        return round(hours, 2)
    except ValueError:
        return fallback or 0
