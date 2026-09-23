# app/services/complaint_service.py

from typing import List, Optional

from app.core.supabase_client import get_supabase_admin_client, get_user_scoped_client
from app.models.complaint import Complaint

TABLE_NAME = "complaints"  # NOTE: assumed table name, pending schema confirmation


def _row_to_complaint(row: dict) -> Complaint:
    return Complaint(**row)


def list_all_complaints_admin() -> List[Complaint]:
    """
    Admin-only: every complaint across all homeowners.
    Caller must already be authorized (require_role) — this function
    performs no authorization check itself.
    """
    client = get_supabase_admin_client()
    response = client.table(TABLE_NAME).select("*").order("created_at", desc=True).execute()
    return [_row_to_complaint(row) for row in response.data]


def list_own_complaints(access_token: str, homeowner_id: str) -> List[Complaint]:
    """
    Homeowner self-view: own complaints only. Uses a user-scoped
    client so RLS enforces this independently of the .eq() filter.
    """
    client = get_user_scoped_client(access_token)
    response = (
        client.table(TABLE_NAME)
        .select("*")
        .eq("homeowner_id", homeowner_id)
        .order("created_at", desc=True)
        .execute()
    )
    return [_row_to_complaint(row) for row in response.data]


def get_complaint_by_id_admin(complaint_id: str) -> Optional[Complaint]:
    """Admin-only: fetch any complaint by id, regardless of owner."""
    client = get_supabase_admin_client()
    response = (
        client.table(TABLE_NAME).select("*").eq("id", complaint_id).limit(1).execute()
    )
    if not response.data:
        return None
    return _row_to_complaint(response.data[0])


def get_own_complaint_by_id(access_token: str, homeowner_id: str, complaint_id: str) -> Optional[Complaint]:
    """
    Homeowner self-view: fetch ONE complaint, but only if it belongs
    to this homeowner. The .eq("homeowner_id", ...) filter combined
    with the user-scoped client (RLS) means a homeowner requesting
    another homeowner's complaint id gets nothing back, not an error
    that leaks whether the id exists.
    """
    client = get_user_scoped_client(access_token)
    response = (
        client.table(TABLE_NAME)
        .select("*")
        .eq("id", complaint_id)
        .eq("homeowner_id", homeowner_id)
        .limit(1)
        .execute()
    )
    if not response.data:
        return None
    return _row_to_complaint(response.data[0])


def create_complaint(access_token: str, homeowner_id: str, data: dict) -> Complaint:
    """
    Homeowner submits a new complaint. Uses the user-scoped client
    (not admin) so this insert is subject to the same RLS policy
    that governs the homeowner's own row-ownership — consistent
    with how reads are scoped, rather than mixing an admin-client
    write into an otherwise user-scoped flow.
    """
    complaint_data = {**data, "homeowner_id": homeowner_id, "status": "Submitted"}
    client = get_user_scoped_client(access_token)
    response = client.table(TABLE_NAME).insert(complaint_data).execute()
    return _row_to_complaint(response.data[0])


def update_complaint_status_admin(complaint_id: str, status: str) -> Optional[Complaint]:
    """Admin-only: move a complaint through its status lifecycle."""
    client = get_supabase_admin_client()
    response = (
        client.table(TABLE_NAME)
        .update({"status": status})
        .eq("id", complaint_id)
        .execute()
    )
    if not response.data:
        return None
    return _row_to_complaint(response.data[0])