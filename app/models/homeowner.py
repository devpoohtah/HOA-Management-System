# app/models/homeowner.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class Homeowner:
    """
    Internal representation of a homeowner record, as returned from
    Supabase.

    NOTE: table name and exact column set are assumed for now
    ("homeowners": id, user_id, first_name, last_name, email, phone,
    block, lot, role, is_active, created_at, updated_at). Pending
    real schema review.

    role is the source of truth for authorization (see
    app.core.roles / app.core.dependencies.get_user_role) — NOT
    Supabase Auth app_metadata. Storing it here lets an admin role
    be reassigned through ordinary app CRUD (e.g. after an HOA
    election) instead of calling Supabase's admin auth API.
    """

    id: str
    user_id: str  # Supabase Auth user id this record is linked to
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    block: Optional[str] = None
    lot: Optional[str] = None
    role: str = "homeowner"  # "homeowner" | "admin"
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"