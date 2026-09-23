# app/services/dues_service.py

from typing import List, Optional

from app.core.supabase_client import get_supabase_admin_client, get_user_scoped_client
from app.models.assessment import Assessment

TABLE_NAME = "assessments"  # NOTE: assumed table name, pending schema confirmation


def _row_to_assessment(row: dict) -> Assessment:
    return Assessment(**row)


def list_all_assessments_admin() -> List[Assessment]:
    """
    Admin-only: every assessment across all homeowners.
    Caller must already be authorized (require_role) — this function
    performs no authorization check itself.
    """
    client = get_supabase_admin_client()
    response = client.table(TABLE_NAME).select("*").order("due_date").execute()
    return [_row_to_assessment(row) for row in response.data]


def list_assessments_by_status_admin(status: str) -> List[Assessment]:
    """
    Admin-only: assessments filtered by status ("UNPAID" or "PAID").
    Used for the delinquent/unpaid-only view on /dues. Filtering
    happens at the database (.eq), not by pulling every row and
    discarding most of them in Python.
    """
    client = get_supabase_admin_client()
    response = (
        client.table(TABLE_NAME)
        .select("*")
        .eq("status", status)
        .order("due_date")
        .execute()
    )
    return [_row_to_assessment(row) for row in response.data]


def list_assessments_for_homeowner_admin(homeowner_id: str) -> List[Assessment]:
    """Admin-only: assessments for one specific homeowner."""
    client = get_supabase_admin_client()
    response = (
        client.table(TABLE_NAME)
        .select("*")
        .eq("homeowner_id", homeowner_id)
        .order("due_date")
        .execute()
    )
    return [_row_to_assessment(row) for row in response.data]


def list_own_assessments(access_token: str, homeowner_id: str) -> List[Assessment]:
    """
    Homeowner self-view: own assessments only. Uses a user-scoped
    client so RLS enforces this independently of the .eq() filter.
    """
    client = get_user_scoped_client(access_token)
    response = (
        client.table(TABLE_NAME)
        .select("*")
        .eq("homeowner_id", homeowner_id)
        .order("due_date")
        .execute()
    )
    return [_row_to_assessment(row) for row in response.data]


def create_assessment_admin(data: dict) -> Assessment:
    """Admin-only: create a new assessment. Status always starts UNPAID."""
    data = {**data, "status": "UNPAID"}
    client = get_supabase_admin_client()
    response = client.table(TABLE_NAME).insert(data).execute()
    return _row_to_assessment(response.data[0])


def get_assessment_by_id_admin(assessment_id: str) -> Optional[Assessment]:
    client = get_supabase_admin_client()
    response = (
        client.table(TABLE_NAME).select("*").eq("id", assessment_id).limit(1).execute()
    )
    if not response.data:
        return None
    return _row_to_assessment(response.data[0])


def mark_assessment_paid_admin(assessment_id: str) -> Optional[Assessment]:
    """
    Admin-only: marks an assessment PAID. Called by payment_service
    after a payment covering it is recorded — not meant to be called
    directly from a route.
    """
    client = get_supabase_admin_client()
    response = (
        client.table(TABLE_NAME)
        .update({"status": "PAID"})
        .eq("id", assessment_id)
        .execute()
    )
    if not response.data:
        return None
    return _row_to_assessment(response.data[0])