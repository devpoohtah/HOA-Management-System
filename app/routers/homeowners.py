# app/routers/homeowners.py

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from typing import Optional

from app.core.templates import templates
from app.core.dependencies import require_authenticated, require_role
from app.core.security import get_access_token_from_request
from app.services.homeowner_service import (
    list_all_homeowners_admin,
    get_own_homeowner_profile,
    get_homeowner_by_id_admin,
    update_homeowner_admin,
    update_homeowner_role_admin,
    admin_reset_homeowner_password,
    create_homeowner_account_admin,
    RoleChangeNotAllowedError,
    DuplicateHomeownerError,
    AccountCreationError,
)   
from app.schemas.homeowner import HomeownerRoleUpdate, HomeownerAccountCreate, HomeownerUpdate

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

@router.get("/new")
def new_homeowner_form(request: Request, user=Depends(require_role("admin"))):
    return templates.TemplateResponse(
        request=request,
        name="homeowners/new.html",
        context={"error": None, "form": {}},
    )


@router.post("/new")
def create_homeowner_submit(
    request: Request,
    user=Depends(require_role("admin")),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    block: str = Form(None),
    lot: str = Form(None),
    password: str = Form(...),
):
    form_values = {
        "first_name": first_name, "last_name": last_name, "email": email,
        "phone": phone, "block": block, "lot": lot,
    }
    try:
        payload = HomeownerAccountCreate(**form_values, password=password)
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="homeowners/new.html",
            context={"error": str(e), "form": form_values},
        )

    try:
        create_homeowner_account_admin(payload.model_dump(exclude={"password"}), payload.password)
    except DuplicateHomeownerError as e:
        return templates.TemplateResponse(
            request=request,
            name="homeowners/new.html",
            context={"error": str(e), "form": form_values},
        )
    except AccountCreationError as e:
        return templates.TemplateResponse(
            request=request,
            name="homeowners/new.html",
            context={"error": str(e), "form": form_values},
        )

    return RedirectResponse(url="/homeowners", status_code=303)

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

@router.post("/{homeowner_id}/details")
def update_details_submit(
    request: Request,
    homeowner_id: str,
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone: Optional[str] = Form(None),
    block: Optional[str] = Form(None),
    lot: Optional[str] = Form(None),
    user=Depends(require_role("admin")),
):
    """Admin-only: edit a homeowner's name, phone, block, and lot. Email is not editable here."""
    homeowner = get_homeowner_by_id_admin(homeowner_id)
    if homeowner is None:
        raise HTTPException(status_code=404, detail="Homeowner not found.")

    first_name = first_name.strip()
    last_name = last_name.strip()
    if not first_name or not last_name:
        return templates.TemplateResponse(
            request=request,
            name="homeowners/edit.html",
            context={
                "homeowner": homeowner,
                "current_user_id": user.id,
                "error": None,
                "details_error": "First name and last name cannot be blank.",
            },
            status_code=400,
        )

    validated = HomeownerUpdate(
        first_name=first_name,
        last_name=last_name,
        phone=(phone or "").strip() or None,
        block=(block or "").strip() or None,
        lot=(lot or "").strip() or None,
    )
    update_homeowner_admin(homeowner_id, validated.model_dump(exclude_unset=True))
    return RedirectResponse(url="/homeowners", status_code=303) 

@router.post("/{homeowner_id}/reset-password")
def reset_password_submit(
    request: Request,
    homeowner_id: str,
    user=Depends(require_role("admin")),
):
    homeowner = get_homeowner_by_id_admin(homeowner_id)
    if homeowner is None:
        raise HTTPException(status_code=404, detail="Homeowner not found.")

    temp_password = admin_reset_homeowner_password(homeowner.user_id)

    return templates.TemplateResponse(
        request=request,
        name="homeowners/edit.html",
        context={
            "homeowner": homeowner,
            "current_user_id": user.id,
            "error": None,
            "temp_password": temp_password,
        },
    )