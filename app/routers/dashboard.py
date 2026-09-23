# app/routers/dashboard.py

from fastapi import APIRouter, Request, Depends

from app.core.templates import templates
from app.core.dependencies import require_authenticated, get_user_role
from app.core.security import get_access_token_from_request
from app.services.financial_summary_service import get_community_financial_summary
from app.services.homeowner_service import get_own_homeowner_profile, list_all_homeowners_admin
from app.services.dues_service import list_own_assessments
from app.services.payment_service import list_own_payments

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(request: Request, user=Depends(require_authenticated)):
    role = get_user_role(user)
    summary = get_community_financial_summary()

    if role == "admin":
        total_homeowners = len(list_all_homeowners_admin())
        return templates.TemplateResponse(
            request=request,
            name="dashboard/admin_dashboard.html",
            context={"summary": summary, "total_homeowners": total_homeowners},
        )

    access_token = get_access_token_from_request(request)
    homeowner = get_own_homeowner_profile(access_token=access_token, user_id=user.id)

    own_outstanding = 0
    last_payment = None

    if homeowner is not None:
        assessments = list_own_assessments(access_token=access_token, homeowner_id=homeowner.id)
        own_outstanding = sum(a.amount for a in assessments if a.status == "UNPAID")

        payments = list_own_payments(access_token=access_token, homeowner_id=homeowner.id)
        if payments:
            last_payment = payments[0]

    return templates.TemplateResponse(
        request=request,
        name="dashboard/homeowner_dashboard.html",
        context={
            "summary": summary,
            "own_outstanding": own_outstanding,
            "last_payment": last_payment,
        },
    )