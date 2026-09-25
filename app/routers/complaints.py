from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse

from app.core.templates import templates
from app.core.dependencies import require_authenticated, require_role, get_user_role
from app.core.roles import role_meets_minimum
from app.core.security import get_access_token_from_request
from app.services.complaint_service import (
    list_all_complaints_admin,
    list_own_complaints,
    get_complaint_by_id_admin,
    get_own_complaint_by_id,
    create_complaint,
    update_complaint_status_admin,
)
from app.services.homeowner_service import (
    get_own_homeowner_profile,
    get_homeowner_by_id_admin,
    list_all_homeowners_admin,
)
from app.schemas.complaint import ComplaintCreate, ComplaintStatusUpdate

router = APIRouter(prefix="/complaints", tags=["complaints"])

def _submitter_label(homeowner):
    """'Juan Cruz (Block 3, Lot 7)' — so the admin can tell who submitted a complaint."""
    place = ", ".join(
        p for p in (
            f"Block {homeowner.block}" if homeowner.block else "",
            f"Lot {homeowner.lot}" if homeowner.lot else "",
        ) if p
    )
    return f"{homeowner.full_name} ({place})" if place else homeowner.full_name

@router.get("")
def complaints_list(request: Request, user=Depends(require_authenticated)):
    role = get_user_role(user)

    if role_meets_minimum(role, "admin"):
        complaints = list_all_complaints_admin()
        submitter_labels = {h.id: _submitter_label(h) for h in list_all_homeowners_admin()}
        return templates.TemplateResponse(
            request=request,
            name="complaints/list.html",
            context={
                "complaints": complaints,
                "submitter_labels": submitter_labels,
                "is_admin_view": True,
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

    complaints = list_own_complaints(access_token=access_token, homeowner_id=homeowner.id)
    return templates.TemplateResponse(
        request=request,
        name="complaints/list.html",
        context={
            "complaints": complaints,
            "is_admin_view": False,
            "base_template": "homeowner_base.html",
        },
    )


@router.get("/submit")
def submit_complaint_form(request: Request, user=Depends(require_authenticated)):
    return templates.TemplateResponse(
        request=request,
        name="complaints/submit.html",
        context={"error": None},
    )


@router.post("/submit")
def submit_complaint_submit(
    request: Request,
    category: str = Form(...),
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

    data = ComplaintCreate(category=category, description=description).model_dump()
    complaint = create_complaint(access_token=access_token, homeowner_id=homeowner.id, data=data)

    return RedirectResponse(url=f"/complaints/{complaint.id}", status_code=303)


@router.get("/{complaint_id}")
def complaint_detail(request: Request, complaint_id: str, user=Depends(require_authenticated)):
    role = get_user_role(user)
    is_admin_view = role_meets_minimum(role, "admin")

    if is_admin_view:
        complaint = get_complaint_by_id_admin(complaint_id)
    else:
        access_token = get_access_token_from_request(request)
        homeowner = get_own_homeowner_profile(access_token=access_token, user_id=user.id)
        if homeowner is None:
            raise HTTPException(status_code=404, detail="Homeowner record not found.")
        complaint = get_own_complaint_by_id(
            access_token=access_token, homeowner_id=homeowner.id, complaint_id=complaint_id
        )

    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found.")

    submitter = None
    if is_admin_view:
        submitter_homeowner = get_homeowner_by_id_admin(complaint.homeowner_id)
        submitter = _submitter_label(submitter_homeowner) if submitter_homeowner else "Unknown homeowner"

    return templates.TemplateResponse(
        request=request,
        name="complaints/detail.html",
        context={
            "complaint": complaint,
            "submitter": submitter,
            "is_admin_view": is_admin_view,
            "base_template": "admin_base.html" if is_admin_view else "homeowner_base.html",
        },
    )


@router.post("/{complaint_id}/status")
def update_complaint_status(
    request: Request,
    complaint_id: str,
    status: str = Form(...),
    user=Depends(require_role("admin")),
):
    validated = ComplaintStatusUpdate(status=status)
    update_complaint_status_admin(complaint_id, validated.status)
    return RedirectResponse(url=f"/complaints/{complaint_id}", status_code=303)