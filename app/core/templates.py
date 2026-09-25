# app/core/templates.py

from datetime import datetime

from fastapi.templating import Jinja2Templates

# Shared Jinja2 template engine instance.
# Imported by main.py (to attach it to the app) and by any router
# that needs to render an HTML page (e.g. auth, dashboard).
templates = Jinja2Templates(directory="templates")


def format_datetime(value):
    """
    Supabase timestamp columns (e.g. announcements.created_at) come back
    as raw ISO strings like '2026-09-23T10:23:10.223049+00:00'. This
    turns that into 'September 23, 2026' for display. Falsy input
    (None, "") passes through unchanged so `{{ value|format_datetime or "" }}`
    keeps working the same way `{{ value or "" }}` did before.
    """
    if not value:
        return value
    try:
        dt = datetime.fromisoformat(str(value))
    except (ValueError, TypeError):
        return value
    return f"{dt.strftime('%B')} {dt.day}, {dt.year}"


ANNOUNCEMENT_CATEGORY_LABELS = {
    "meeting": "Meeting",
    "water_interruption": "Water Interruption",
    "road_maintenance": "Road Maintenance",
    "garbage_collection": "Garbage Collection",
    "security": "Security Notice",
    "dues_reminder": "Dues Reminder",
    "general": "Community Notice",
}


def category_label(value):
    """'water_interruption' -> 'Water Interruption'. Falls back to the raw
    value if it's not one of the known announcement categories."""
    return ANNOUNCEMENT_CATEGORY_LABELS.get(value, value)


templates.env.filters["format_datetime"] = format_datetime
templates.env.filters["category_label"] = category_label