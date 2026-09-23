# app/routers/homeowners.py

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse

from app.core.templates import templates
from app.core.dependencies import require_authenticated, require_role
from app.core.security import get_access_token_from_request
from app.services.homeowner_service import (
    list_all_homeowners_admin,
    get_own_homeowner_profile,
    get_homeowner_by_id_admin,
    update_homeowner_role_admin,
    RoleChangeNotAllowedError,
)
from app.schemas.homeowner import HomeownerRoleUpdate

router = APIRouter(prefix="/homeowners", tags=["homeowners"])


@router.get("")
def homeowners_list(request: Request, user=Depends(require_role("admin"))):
    """
    Admin-only directory of all homeowners, including their role and
    a "Manage Role" action. Since this whole route already requires
    admin, no separate flag is needed to decide whether to show that
    action — every viewer here is already an admin.
    """
    homeowners = list_all_homeowners_admin()
    return templates.TemplateResponse(
        request=request,
        name="homeowners/list.html",
        context={"homeowners": homeowners},
    )


@router.get("/me")
def my_profile(request: Request, user=Depends(require_authenticated)):
    """A homeowner's own profile page."""
    access_token = get_access_token_from_request(request)
    homeowner = get_own_homeowner_profile(access_token=access_token, user_id=user.id)

    if homeowner is None:
        raise HTTPException(
            status_code=404,
            detail="No homeowner record is linked to your account yet. "
                   "Please contact the HOA secretary.",
        )

    return templates.TemplateResponse(
        request=request,
        name="homeowners/profile.html",
        context={"homeowner": homeowner},
    )


@router.get("/{homeowner_id}/role")
def edit_role_form(request: Request, homeowner_id: str, user=Depends(require_role("admin"))):
    """Admin-only: change a homeowner's role."""
    homeowner = get_homeowner_by_id_admin(homeowner_id)
    if homeowner is None:
        raise HTTPException(status_code=404, detail="Homeowner not found.")

    return templates.TemplateResponse(
        request=request,
        name="homeowners/edit.html",
        context={"homeowner": homeowner, "current_user_id": user.id, "error": None},
    )


@router.post("/{homeowner_id}/role")
def update_role_submit(
    request: Request,
    homeowner_id: str,
    role: str = Form(...),
    user=Depends(require_role("admin")),
):
    validated = HomeownerRoleUpdate(role=role)

    try:
        update_homeowner_role_admin(homeowner_id, validated.role, acting_user_id=user.id)
    except RoleChangeNotAllowedError as e:
        homeowner = get_homeowner_by_id_admin(homeowner_id)
        return templates.TemplateResponse(
            request=request,
            name="homeowners/edit.html",
            context={"homeowner": homeowner, "current_user_id": user.id, "error": str(e)},
            status_code=403,
        )

    return RedirectResponse(url="/homeowners", status_code=303)