# app/services/announcement_service.py

from typing import List, Optional

from app.core.supabase_client import get_supabase_admin_client
from app.models.announcement import Announcement

TABLE_NAME = "announcements"  # NOTE: assumed table name, pending schema confirmation


def _row_to_announcement(row: dict) -> Announcement:
    return Announcement(**row)


def list_all_announcements() -> List[Announcement]:
    """
    Announcements have no per-homeowner privacy concern, so this is
    used for both the admin list and the homeowner-facing view —
    unlike payments/dues, there's no separate "own records" query
    needed here.
    """
    client = get_supabase_admin_client()
    response = client.table(TABLE_NAME).select("*").order("created_at", desc=True).execute()
    return [_row_to_announcement(row) for row in response.data]


def get_announcement_by_id(announcement_id: str) -> Optional[Announcement]:
    client = get_supabase_admin_client()
    response = (
        client.table(TABLE_NAME)
        .select("*")
        .eq("id", announcement_id)
        .limit(1)
        .execute()
    )
    if not response.data:
        return None
    return _row_to_announcement(response.data[0])


def create_announcement_admin(data: dict, published_by: str) -> Announcement:
    """Admin-only: publish a new announcement."""
    announcement_data = {**data, "published_by": published_by}
    client = get_supabase_admin_client()
    response = client.table(TABLE_NAME).insert(announcement_data).execute()
    return _row_to_announcement(response.data[0])


def update_announcement_admin(announcement_id: str, data: dict) -> Announcement:
    """Admin-only: edit an existing announcement's title/content/category."""
    client = get_supabase_admin_client()
    response = (
        client.table(TABLE_NAME)
        .update(data)
        .eq("id", announcement_id)
        .execute()
    )
    return _row_to_announcement(response.data[0])


def delete_announcement_admin(announcement_id: str) -> None:
    """Admin-only: permanently remove an announcement."""
    client = get_supabase_admin_client()
    client.table(TABLE_NAME).delete().eq("id", announcement_id).execute()
    
