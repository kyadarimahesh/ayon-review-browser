import re
from datetime import datetime, timedelta


def standardize_date(date_str):
    """Convert various date formats to YYYY-MM-DD HH:MM using simple regex"""
    if not date_str or date_str == "N/A":
        return "N/A"

    try:
        # Handle ISO format: 2025-05-30T18:18:42.398552+05:30
        iso_match = re.match(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})', str(date_str))
        if iso_match:
            year, month, day, hour, minute, second = iso_match.groups()
            return f"{year}-{month}-{day} {hour}:{minute}"

        # Handle simple format: 2025-09-17 15:53:18
        simple_match = re.match(r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})', str(date_str))
        if simple_match:
            year, month, day, hour, minute, second = simple_match.groups()
            return f"{year}-{month}-{day} {hour}:{minute}"

        # Handle date only: 2025-09-17
        date_only_match = re.match(r'(\d{4})-(\d{2})-(\d{2})', str(date_str))
        if date_only_match:
            year, month, day = date_only_match.groups()
            return f"{year}-{month}-{day} 00:00"

        return "N/A"
    except:
        return "N/A"


def parse_date_simple(date_str):
    """Parse standardized date string to datetime object"""
    if not date_str or date_str == "N/A":
        return None

    try:
        # Parse YYYY-MM-DD HH:MM format
        match = re.match(r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})', date_str)
        if match:
            year, month, day, hour, minute = map(int, match.groups())
            return datetime(year, month, day, hour, minute)
        return None
    except:
        return None


def filter_by_date_simple(items, date_filter="ALL"):
    """Filter items by date range using simple date parsing"""
    if date_filter == "ALL":
        return items

    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if date_filter == "Today":
        start_date = today_start
        end_date = today_start + timedelta(days=1)
    elif date_filter == "Yesterday":
        start_date = today_start - timedelta(days=1)
        end_date = today_start
    elif date_filter == "Last 7 days":
        start_date = today_start - timedelta(days=7)
        end_date = today_start + timedelta(days=1)
    else:
        return items

    filtered_items = []
    for item in items:
        date_field = item.get("submitted_at") or item.get("created_at")
        if date_field and date_field != "N/A":
            item_date = parse_date_simple(date_field)
            if item_date and start_date <= item_date < end_date:
                filtered_items.append(item)

    return filtered_items