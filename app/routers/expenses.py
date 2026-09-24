from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from typing import Optional

from app.core.templates import templates
from app.core.dependencies import require_role, require_authenticated
from app.services.expense_service import (
    list_all_expenses_admin,
    list_all_expenses_public,
    get_expense_totals_by_category,
    create_expense_admin,
)
from app.services.project_service import list_all_projects
from app.schemas.expense import ExpenseCreate

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("")
def expenses_list_admin(request: Request, user=Depends(require_role("admin"))):
    expenses = list_all_expenses_admin()
    return templates.TemplateResponse(
        request=request,
        name="expenses/list.html",
        context={
            "expenses": expenses,
            "is_admin_view": True,
            "base_template": "admin_base.html",
        },
    )


@router.get("/public")
def expenses_list_public(request: Request, user=Depends(require_authenticated)):
    expenses = list_all_expenses_public()
    return templates.TemplateResponse(
        request=request,
        name="expenses/list.html",
        context={
            "expenses": expenses,
            "is_admin_view": False,
            "base_template": "base.html",
        },
    )


@router.get("/record")
def record_expense_form(request: Request, user=Depends(require_role("admin"))):
    projects = list_all_projects()
    return templates.TemplateResponse(
        request=request,
        name="expenses/record.html",
        context={"projects": projects, "error": None},
    )


@router.post("/record")
def record_expense_submit(
    request: Request,
    category: str = Form(...),
    description: str = Form(...),
    amount: float = Form(...),
    expense_date: str = Form(...),
    vendor: Optional[str] = Form(None),
    receipt_url: Optional[str] = Form(None),
    project_id: Optional[str] = Form(None),
    user=Depends(require_role("admin")),
):
    expense_data = ExpenseCreate(
        category=category,
        description=description,
        amount=amount,
        expense_date=expense_date,
        vendor=vendor,
        receipt_url=receipt_url,
        project_id=project_id or None,
    ).model_dump()

    recorded_by = getattr(user, "id", "unknown")
    create_expense_admin(expense_data, recorded_by=recorded_by)

    return RedirectResponse(url="/expenses", status_code=303)   