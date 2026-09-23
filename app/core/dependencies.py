# app/core/dependencies.py

from fastapi import Request, HTTPException

from app.core.security import get_current_user
from app.core.roles import role_meets_minimum


def require_authenticated(request: Request):
    """
    FastAPI dependency. Ensures a request has a valid, logged-in
    Supabase session. If not, redirects to the login page.
    """
    user = get_current_user(request)
    if user is None:
        raise HTTPException(
            status_code=303,
            headers={"Location": "/login"},
        )
    return user


def get_user_role(user) -> str:
    """
    Looks up the CURRENT role for this user from the database
    (homeowners.role) — NOT Supabase Auth app_metadata. This is what
    lets an admin role be reassigned dynamically (e.g. after an HOA
    election) through ordinary app CRUD, instead of requiring calls
    to Supabase's admin auth API.

    Defaults to "homeowner" if no homeowner record exists yet, or
    the record has no role set.
    """
    from app.services.homeowner_service import get_homeowner_role_by_user_id

    role = get_homeowner_role_by_user_id(user.id)
    return role or "homeowner"


def require_role(minimum_role: str):
    """
    Dependency FACTORY for role-gated routes, e.g.:

        @router.get("/admin/payments")
        def admin_payments(user = Depends(require_role("admin"))):
            ...
    """

    def dependency(request: Request):
        user = require_authenticated(request)
        role = get_user_role(user)

        if not role_meets_minimum(role, minimum_role):
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource.",
            )

        return user

    return dependency