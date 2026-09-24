# app/schemas/homeowner.py

from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class HomeownerBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    block: Optional[str] = None
    lot: Optional[str] = None


class HomeownerCreate(HomeownerBase):
    """
    Used by an admin/secretary to provision a new homeowner record,
    linked to an existing Supabase Auth user. Role always starts as
    "homeowner" — promotion is a separate action, not part of
    initial provisioning.
    """
    user_id: str


class HomeownerAccountCreate(HomeownerBase):
    """
    Used by an admin/secretary to create a brand-new homeowner
    ACCOUNT from scratch — both the Supabase Auth login and the
    homeowners record, in one step. Unlike HomeownerCreate, there is
    no existing user_id yet; the Auth user is created as part of
    this same flow (see homeowner_service.create_homeowner_account_admin).
    """
    password: str = Field(min_length=8)


class HomeownerUpdate(BaseModel):
    """
    All fields optional — partial update. Excludes user_id, email,
    and role intentionally: role changes go through
    HomeownerRoleUpdate, kept separate from routine contact-info edits.
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    block: Optional[str] = None
    lot: Optional[str] = None
    is_active: Optional[bool] = None


class HomeownerRoleUpdate(BaseModel):
    """
    Admin-only: reassign a homeowner's role. See
    app.services.homeowner_service.update_homeowner_role_admin for
    the "can't demote another admin" business rule enforced on top
    of this schema.
    """
    role: Literal["homeowner", "admin"]


class HomeownerOut(HomeownerBase):
    """
    Response shape. Deliberately omits user_id — no route currently
    needs to expose the raw auth-user linkage to a template.
    """
    id: str
    role: str
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True) 