# app/routers/dues.py

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from typing import Optional

from app.core.templates import templates
from app.core.dependencies import require_authenticated, require_role
from app.core.security import get_access_token_from_request
from app.services.dues_service import (
    list_all_assessments_admin,
    list_assessments_by_status_admin,
    list_own_assessments,
    create_assessment_admin,
)
from app.services.homeowner_service import get_own_homeowner_profile, list_all_homeowners_admin
from app.schemas.assessment import AssessmentCreate

router = APIRouter(prefix="/dues", tags=["dues"])


@router.get("")
def dues_list_admin(
    request: Request,
    status_filter: Optional[str] = None,
    user=Depends(require_role("admin")),
):
    """
    Admin-only: assessments across all homeowners. Pass
    ?status_filter=UNPAID or ?status_filter=PAID to narrow the list
    (e.g. delinquent-only view). Any other/missing value shows all.
    """
    if status_filter in ("UNPAID", "PAID"):
        assessments = list_assessments_by_status_admin(status_filter)
    else:
        assessments = list_all_assessments_admin()

    return templates.TemplateResponse(
        request=request,
        name="dues/list.html",
        context={"assessments": assessments, "status_filter": status_filter},
    )


@router.get("/new")
def new_assessment_form(request: Request, user=Depends(require_role("admin"))):
    """
    Admin-only: form to generate a new due/assessment for a
    homeowner (regular monthly due or special assessment).
    """
    homeowners = list_all_homeowners_admin()
    return templates.TemplateResponse(
        request=request,
        name="dues/create.html",
        context={"homeowners": homeowners, "error": None},
    )


@router.post("/new")
def new_assessment_submit(
    request: Request,
    homeowner_id: str = Form(...),
    assessment_type: str = Form("regular"),
    description: str = Form(...),
    amount: float = Form(...),
    period_label: Optional[str] = Form(None),
    due_date: Optional[str] = Form(None),
    user=Depends(require_role("admin")),
):
    data = AssessmentCreate(
        homeowner_id=homeowner_id,
        assessment_type=assessment_type,
        description=description,
        amount=amount,
        period_label=period_label,
        due_date=due_date,
    ).model_dump()

    create_assessment_admin(data)
    return RedirectResponse(url="/dues", status_code=303)


@router.get("/me")
def my_dues(request: Request, user=Depends(require_authenticated)):
    """Homeowner self-view: own assessments + computed outstanding total."""
    access_token = get_access_token_from_request(request)
    homeowner = get_own_homeowner_profile(access_token=access_token, user_id=user.id)

    if homeowner is None:
        raise HTTPException(
            status_code=404,
            detail="No homeowner record is linked to your account yet. "
                   "Please contact the HOA secretary.",
        )

    assessments = list_own_assessments(access_token=access_token, homeowner_id=homeowner.id)
    outstanding_total = sum(a.amount for a in assessments if a.status == "UNPAID")

    return templates.TemplateResponse(
        request=request,
        name="dues/detail.html",
        context={
            "homeowner": homeowner,
            "assessments": assessments,
            "outstanding_total": outstanding_total,
        },
    )