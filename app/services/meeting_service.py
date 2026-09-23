# app/services/meeting_service.py

from typing import List, Optional

from app.core.supabase_client import get_supabase_admin_client
from app.models.meeting import Meeting

TABLE_NAME = "meetings"  # NOTE: assumed table name, pending schema confirmation


def _row_to_meeting(row: dict) -> Meeting:
    return Meeting(**row)


def list_all_meetings() -> List[Meeting]:
    """
    Meetings have no per-homeowner privacy concern, so this single
    function serves both the admin and homeowner-facing list.
    """
    client = get_supabase_admin_client()
    response = client.table(TABLE_NAME).select("*").order("meeting_date", desc=True).execute()
    return [_row_to_meeting(row) for row in response.data]


def get_meeting_by_id(meeting_id: str) -> Optional[Meeting]:
    client = get_supabase_admin_client()
    response = (
        client.table(TABLE_NAME).select("*").eq("id", meeting_id).limit(1).execute()
    )
    if not response.data:
        return None
    return _row_to_meeting(response.data[0])


def create_meeting_admin(data: dict) -> Meeting:
    """Admin-only: schedule a new meeting."""
    meeting_data = {**data, "status": "Upcoming"}
    client = get_supabase_admin_client()
    response = client.table(TABLE_NAME).insert(meeting_data).execute()
    return _row_to_meeting(response.data[0])


def update_meeting_minutes_admin(meeting_id: str, data: dict) -> Optional[Meeting]:
    """
    Admin-only: record minutes/decisions/attendees after a meeting
    takes place. Also flips status to "Completed" — treated as the
    same action, since a meeting with recorded minutes has, by
    definition, already happened.
    """
    update_data = {**data, "status": "Completed"}
    client = get_supabase_admin_client()
    response = (
        client.table(TABLE_NAME).update(update_data).eq("id", meeting_id).execute()
    )
    if not response.data:
        return None
    return _row_to_meeting(response.data[0])    