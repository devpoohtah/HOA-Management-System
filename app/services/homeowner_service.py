# app/services/homeowner_service.py

from typing import List, Optional

from app.core.supabase_client import get_supabase_admin_client, get_user_scoped_client
from app.models.homeowner import Homeowner

TABLE_NAME = "homeowners"  # NOTE: assumed table name, pending schema confirmation


class RoleChangeNotAllowedError(Exception):
    """
    Raised when a requested role change violates the business rule:
    an admin may promote a homeowner to admin, and may demote
    THEMSELVES from admin back to homeowner, but may NOT demote a
    different admin. Prevents any single admin from unilaterally
    removing another admin's access — a handover should be
    voluntary (the outgoing admin steps down), not forced by a peer.
    """
    pass


def _row_to_homeowner(row: dict) -> Homeowner:
    return Homeowner(**row)


def list_all_homeowners_admin() -> List[Homeowner]:
    """Admin-only: full homeowner directory."""
    client = get_supabase_admin_client()
    response = client.table(TABLE_NAME).select("*").order("last_name").execute()
    return [_row_to_homeowner(row) for row in response.data]


def get_homeowner_by_id_admin(homeowner_id: str) -> Optional[Homeowner]:
    """Admin-only: fetch a single homeowner by record id."""
    client = get_supabase_admin_client()
    response = (
        client.table(TABLE_NAME)
        .select("*")
        .eq("id", homeowner_id)
        .limit(1)
        .execute()
    )
    if not response.data:
        return None
    return _row_to_homeowner(response.data[0])


def get_own_homeowner_profile(access_token: str, user_id: str) -> Optional[Homeowner]:
    """
    Homeowner self-view: fetch the record linked to the CURRENTLY
    LOGGED-IN user only. Uses a user-scoped client so RLS enforces
    this independently of the .eq() filter.
    """
    client = get_user_scoped_client(access_token)
    response = (
        client.table(TABLE_NAME)
        .select("*")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if not response.data:
        return None
    return _row_to_homeowner(response.data[0])


def get_homeowner_role_by_user_id(user_id: str) -> Optional[str]:
    """
    Looks up ONLY the role column for a given Supabase Auth user_id.
    Called on every role-gated request via
    app.core.dependencies.get_user_role, so this is a narrow query
    (select role only), not a full profile fetch.

    Uses the ADMIN client deliberately: this function IS the
    authorization mechanism — it can't depend on a user-scoped,
    RLS-gated query, since that would require already knowing the
    user's permissions to read their own role (circular).
    """
    client = get_supabase_admin_client()
    response = (
        client.table(TABLE_NAME)
        .select("role")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if not response.data:
        return None
    return response.data[0].get("role")


def create_homeowner_admin(data: dict) -> Homeowner:
    """
    Admin-only: provision a new homeowner record. Role always starts
    as "homeowner" regardless of what's in data — promotion is a
    separate action.
    """
    data = {**data, "role": "homeowner"}
    client = get_supabase_admin_client()
    response = client.table(TABLE_NAME).insert(data).execute()
    return _row_to_homeowner(response.data[0])


def update_homeowner_admin(homeowner_id: str, data: dict) -> Optional[Homeowner]:
    """
    Admin-only: partial update of a homeowner's contact info. Expects
    data already validated via schemas.homeowner.HomeownerUpdate,
    which excludes role — see update_homeowner_role_admin for that.
    """
    client = get_supabase_admin_client()
    response = (
        client.table(TABLE_NAME).update(data).eq("id", homeowner_id).execute()
    )
    if not response.data:
        return None
    return _row_to_homeowner(response.data[0])


def update_homeowner_role_admin(homeowner_id: str, new_role: str, acting_user_id: str) -> Optional[Homeowner]:
    """
    Admin-only: reassign a homeowner's role. Route-level
    authorization (require_role("admin")) must already gate access
    to this function — it performs no authentication check itself.

    BUSINESS RULE enforced here: if the target homeowner is
    CURRENTLY an admin and new_role would demote them, this is only
    allowed if the person making the change IS that same homeowner
    (acting_user_id == target.user_id) — i.e. an admin can step
    down, but cannot be forced out by another admin. Raises
    RoleChangeNotAllowedError otherwise.

    Promoting a homeowner to admin has no such restriction — any
    current admin can do that freely.
    """
    target = get_homeowner_by_id_admin(homeowner_id)
    if target is None:
        return None

    is_demotion = target.role == "admin" and new_role != "admin"
    is_self = target.user_id == acting_user_id

    if is_demotion and not is_self:
        raise RoleChangeNotAllowedError(
            "You cannot remove another admin's access. "
            "Only that admin can step down themselves."
        )

    client = get_supabase_admin_client()
    response = (
        client.table(TABLE_NAME).update({"role": new_role}).eq("id", homeowner_id).execute()
    )
    if not response.data:
        return None
    return _row_to_homeowner(response.data[0])