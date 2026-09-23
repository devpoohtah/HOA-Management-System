# app/services/request_service.py

from typing import List, Optional

from app.core.supabase_client import get_supabase_admin_client, get_user_scoped_client
from app.models.request import HOARequest

TABLE_NAME = "requests"  # NOTE: assumed table name, pending schema confirmation


def _row_to_request(row: dict) -> HOARequest:
    return HOARequest(**row)


def list_all_requests_admin() -> List[HOARequest]:
    """
    Admin-only: every request across all homeowners.
    Caller must already be authorized (require_role) — this function
    performs no authorization check itself.
    """
    client = get_supabase_admin_client()
    response = client.table(TABLE_NAME).select("*").order("created_at", desc=True).execute()
    return [_row_to_request(row) for row in response.data]


def list_own_requests(access_token: str, homeowner_id: str) -> List[HOARequest]:
    """
    Homeowner self-view: own requests only. Uses a user-scoped
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
    return [_row_to_request(row) for row in response.data]


def get_request_by_id_admin(request_id: str) -> Optional[HOARequest]:
    """Admin-only: fetch any request by id, regardless of owner."""
    client = get_supabase_admin_client()
    response = (
        client.table(TABLE_NAME).select("*").eq("id", request_id).limit(1).execute()
    )
    if not response.data:
        return None
    return _row_to_request(response.data[0])


def get_own_request_by_id(access_token: str, homeowner_id: str, request_id: str) -> Optional[HOARequest]:
    """
    Homeowner self-view: fetch ONE request, but only if it belongs
    to this homeowner — mirrors get_own_complaint_by_id.
    """
    client = get_user_scoped_client(access_token)
    response = (
        client.table(TABLE_NAME)
        .select("*")
        .eq("id", request_id)
        .eq("homeowner_id", homeowner_id)
        .limit(1)
        .execute()
    )
    if not response.data:
        return None
    return _row_to_request(response.data[0])


def create_request(access_token: str, homeowner_id: str, data: dict) -> HOARequest:
    """
    Homeowner submits a new request. Uses the user-scoped client so
    this insert is subject to the same RLS policy that governs the
    homeowner's own row-ownership.
    """
    request_data = {**data, "homeowner_id": homeowner_id, "status": "Submitted"}
    client = get_user_scoped_client(access_token)
    response = client.table(TABLE_NAME).insert(request_data).execute()
    return _row_to_request(response.data[0])


def update_request_status_admin(request_id: str, status: str) -> Optional[HOARequest]:
    """Admin-only: move a request through its status lifecycle."""
    client = get_supabase_admin_client()
    response = (
        client.table(TABLE_NAME)
        .update({"status": status})
        .eq("id", request_id)
        .execute()
    )
    if not response.data:
        return None
    return _row_to_request(response.data[0])