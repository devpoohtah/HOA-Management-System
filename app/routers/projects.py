from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse

from app.core.templates import templates
from app.core.dependencies import require_authenticated, require_role, get_user_role
from app.services.project_service import (
    list_all_projects,
    get_project_by_id,
    get_project_actual_spending,
    create_project_admin,
    update_project_status_admin,
)
from app.services.expense_service import list_expenses_by_project_admin
from app.schemas.project import ProjectCreate, ProjectStatusUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("")
def projects_list(request: Request, user=Depends(require_authenticated)):
    projects = list_all_projects()
    role = get_user_role(user)

    return templates.TemplateResponse(
        request=request,
        name="projects/list.html",
        context={
            "projects": projects,
            "is_admin_view": role == "admin",
            "base_template": "admin_base.html" if role == "admin" else "homeowner_base.html",
        },
    )


@router.get("/new")
def new_project_form(request: Request, user=Depends(require_role("admin"))):
    return templates.TemplateResponse(
        request=request,
        name="projects/new.html",
        context={"error": None},
    )


@router.post("/new")
def new_project_submit(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    budget: float = Form(...),
    start_date: str = Form(None),
    completion_date: str = Form(None),
    user=Depends(require_role("admin")),
):
    data = ProjectCreate(
        name=name,
        description=description,
        budget=budget,
        start_date=start_date or None,
        completion_date=completion_date or None,
    ).model_dump()

    project = create_project_admin(data)
    return RedirectResponse(url=f"/projects/{project.id}", status_code=303)


@router.get("/{project_id}")
def project_detail(request: Request, project_id: str, user=Depends(require_authenticated)):
    project = get_project_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    actual_spending = get_project_actual_spending(project_id)
    related_expenses = list_expenses_by_project_admin(project_id)
    is_admin_view = get_user_role(user) == "admin"

    return templates.TemplateResponse(
        request=request,
        name="projects/detail.html",
        context={
            "project": project,
            "actual_spending": actual_spending,
            "related_expenses": related_expenses,
            "is_admin_view": is_admin_view,
            "base_template": "admin_base.html" if is_admin_view else "base.html",
        },
    )


@router.post("/{project_id}/status")
def update_project_status(
    request: Request,
    project_id: str,
    status: str = Form(...),
    user=Depends(require_role("admin")),
):
    validated = ProjectStatusUpdate(status=status)
    update_project_status_admin(project_id, validated.status)
    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)