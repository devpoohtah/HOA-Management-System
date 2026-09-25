from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse

from app.core.templates import templates
from app.core.dependencies import require_authenticated, require_role, get_user_role
from app.core.security import get_access_token_from_request
from app.services.request_service import (
    list_all_requests_admin,
    list_own_requests,
    get_request_by_id_admin,
    get_own_request_by_id,
    create_request,
    update_request_status_admin,
)
from app.services.homeowner_service import get_own_homeowner_profile, list_all_homeowners_admin
from app.schemas.request import RequestCreate, RequestStatusUpdate

router = APIRouter(prefix="/requests", tags=["requests"])


@router.get("")
def requests_list(request: Request, user=Depends(require_authenticated)):
    role = get_user_role(user)

    if role == "admin":
        req_list = list_all_requests_admin()
        homeowners_by_id = {h.id: h.full_name for h in list_all_homeowners_admin()}
        return templates.TemplateResponse(
            request=request,
            name="requests/list.html",
            context={
                "requests": req_list,
                "is_admin_view": True,
                "homeowners_by_id": homeowners_by_id,
                "base_template": "admin_base.html",
            },
        )

    access_token = get_access_token_from_request(request)
    homeowner = get_own_homeowner_profile(access_token=access_token, user_id=user.id)
    if homeowner is None:
        raise HTTPException(
            status_code=404,
            detail="No homeowner record is linked to your account yet. "
                   "Please contact the HOA secretary.",
        )

    req_list = list_own_requests(access_token=access_token, homeowner_id=homeowner.id)
    return templates.TemplateResponse(
        request=request,
        name="requests/list.html",
        context={
            "requests": req_list,
            "is_admin_view": False,
              "base_template": "homeowner_base.html",
        },
    )


@router.get("/submit")
def submit_request_form(request: Request, user=Depends(require_authenticated)):
    return templates.TemplateResponse(
        request=request,
        name="requests/submit.html",
        context={"error": None},
    )


@router.post("/submit")
def submit_request_submit(
    request: Request,
    request_type: str = Form(...),
    description: str = Form(...),
    user=Depends(require_authenticated),
):
    access_token = get_access_token_from_request(request)
    homeowner = get_own_homeowner_profile(access_token=access_token, user_id=user.id)
    if homeowner is None:
        raise HTTPException(
            status_code=404,
            detail="No homeowner record is linked to your account yet. "
                   "Please contact the HOA secretary.",
        )

    data = RequestCreate(request_type=request_type, description=description).model_dump()
    new_request = create_request(access_token=access_token, homeowner_id=homeowner.id, data=data)

    return RedirectResponse(url=f"/requests/{new_request.id}", status_code=303)


@router.get("/{request_id}")
def request_detail(request: Request, request_id: str, user=Depends(require_authenticated)):
    role = get_user_role(user)
    is_admin_view = role == "admin"

    if is_admin_view:
        req = get_request_by_id_admin(request_id)
    else:
        access_token = get_access_token_from_request(request)
        homeowner = get_own_homeowner_profile(access_token=access_token, user_id=user.id)
        if homeowner is None:
            raise HTTPException(status_code=404, detail="Homeowner record not found.")
        req = get_own_request_by_id(
            access_token=access_token, homeowner_id=homeowner.id, request_id=request_id
        )

    if req is None:
        raise HTTPException(status_code=404, detail="Request not found.")

    requester_name = None
    if is_admin_view:
        homeowners_by_id = {h.id: h.full_name for h in list_all_homeowners_admin()}
        requester_name = homeowners_by_id.get(req.homeowner_id, req.homeowner_id)

    return templates.TemplateResponse(
        request=request,
        name="requests/detail.html",
        context={
            "req": req,
            "is_admin_view": is_admin_view,
            "requester_name": requester_name,
            "base_template": "admin_base.html" if is_admin_view else "base.html",
        },
    )


@router.post("/{request_id}/status")
def update_request_status(
    request: Request,
    request_id: str,
    status: str = Form(...),
    user=Depends(require_role("admin")),
):
    validated = RequestStatusUpdate(status=status)
    update_request_status_admin(request_id, validated.status)
    return RedirectResponse(url=f"/requests/{request_id}", status_code=303)