# app/models/meeting.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class Meeting:
    """
    HOA meeting (upcoming or past).

    NOTE: table/column names assumed ("meetings": id, title,
    meeting_date, meeting_time, location, agenda, minutes,
    decisions, attendees, status, created_at, updated_at). Pending
    real schema review.

    minutes/decisions/attendees are nullable — filled in AFTER the
    meeting happens, not at creation time. attendees is a plain text
    field (not a relational attendee list) per "keep it practical."

    status is an INVENTED two-value lifecycle (Upcoming/Completed) —
    your spec did not define meeting statuses explicitly.
    """

    id: str
    title: str
    meeting_date: str
    location: str
    agenda: str
    meeting_time: Optional[str] = None
    minutes: Optional[str] = None
    decisions: Optional[str] = None
    attendees: Optional[str] = None
    status: str = "Upcoming"  # Upcoming | Completed
    created_at: Optional[str] = None
    updated_at: Optional[str] = None