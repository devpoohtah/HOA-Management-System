# app/routers/payments.py

from typing import Optional, List

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse

from app.core.templates import templates
from app.core.dependencies import require_authenticated, require_role
from app.core.security import get_access_token_from_request
from app.services.payment_service import (
    list_all_payments_admin,
    list_own_payments,
    record_payment_admin,
)
from app.services.homeowner_service import list_all_homeowners_admin, get_own_homeowner_profile
from app.services.dues_service import list_all_assessments_admin, list_own_assessments
from app.schemas.payment import PaymentCreate

router = APIRouter(prefix="/payments", tags=["payments"])

def _assessment_labels(assessments):
    """Map assessment id -> 'Description — Period' so payment lists can show what each payment covers."""
    return {
        a.id: (f"{a.description} — {a.period_label}" if a.period_label else a.description)
        for a in assessments
    }

@router.get("")
def payments_list_admin(request: Request, user=Depends(require_role("admin"))):
    payments = list_all_payments_admin()
    homeowners = list_all_homeowners_admin()
    homeowner_names = {h.id: h.full_name for h in homeowners}
    # recorded_by stores the Supabase Auth user id of whoever recorded the payment
    recorder_names = {h.user_id: h.full_name for h in homeowners}
    assessment_labels = _assessment_labels(list_all_assessments_admin())
    return templates.TemplateResponse(
        request=request,
        name="payments/list.html",
        context={
            "payments": payments,
            "homeowner_names": homeowner_names,
            "recorder_names": recorder_names,
            "assessment_labels": assessment_labels,
        },
    )


@router.get("/record")
def record_payment_form(request: Request, user=Depends(require_role("admin"))):
    """Form for the secretary/admin to manually record a cash payment."""
    homeowners = list_all_homeowners_admin()
    assessments = [a for a in list_all_assessments_admin() if a.status == "UNPAID"]
    return templates.TemplateResponse(
        request=request,
        name="payments/record.html",
        context={"homeowners": homeowners, "assessments": assessments, "error": None},
    )


@router.post("/record")
def record_payment_submit(
    request: Request,
    homeowner_id: str = Form(...),
    assessment_ids: List[str] = Form(default=[]),
    amount: float = Form(...),
    payment_date: str = Form(...),
    payment_method: str = Form("cash"),
    reference_number: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    user=Depends(require_role("admin")),
):
    recorded_by = getattr(user, "id", "unknown")
    assessment_ids = [a for a in assessment_ids if a]

    if assessment_ids:
        assessments = {a.id: a for a in list_all_assessments_admin() if a.id in assessment_ids}
        for aid in assessment_ids:
            assessment = assessments.get(aid)
            if assessment is None:
                continue
            payment_data = PaymentCreate(
                homeowner_id=homeowner_id,
                assessment_id=aid,
                amount=assessment.amount,
                payment_date=payment_date,
                payment_method=payment_method,
                reference_number=reference_number,
                notes=notes,
            ).model_dump()
            record_payment_admin(payment_data, recorded_by=recorded_by)
    else:
        payment_data = PaymentCreate(
            homeowner_id=homeowner_id,
            assessment_id=None,
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            reference_number=reference_number,
            notes=notes,
        ).model_dump()
        record_payment_admin(payment_data, recorded_by=recorded_by)

    return RedirectResponse(url="/payments", status_code=303)


@router.get("/me")
def my_payment_history(request: Request, user=Depends(require_authenticated)):
    access_token = get_access_token_from_request(request)
    homeowner = get_own_homeowner_profile(access_token=access_token, user_id=user.id)

    if homeowner is None:
        raise HTTPException(
            status_code=404,
            detail="No homeowner record is linked to your account yet. "
                   "Please contact the HOA secretary.",
        )

    payments = list_own_payments(access_token=access_token, homeowner_id=homeowner.id)
    assessment_labels = _assessment_labels(
        list_own_assessments(access_token=access_token, homeowner_id=homeowner.id)
    )
    return templates.TemplateResponse(
        request=request,
        name="payments/history.html",
        context={"homeowner": homeowner, "payments": payments, "assessment_labels": assessment_labels},
    )