# app/routers/pages.py

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.core.templates import templates
from app.core.security import get_current_user
from app.services.project_service import list_all_projects, get_project_actual_spending
from app.services.announcement_service import list_all_announcements

router = APIRouter(tags=["pages"])


@router.get("/")
def landing_page(request: Request):
    """
    Public landing page — no login required. If the visitor already
    has a valid session, skip the marketing page and send them
    straight to their dashboard instead of showing it every time.
    """
    user = get_current_user(request)
    if user is not None:
        return RedirectResponse(url="/dashboard", status_code=303)

    # Show a handful of the most recently active projects — not the
    # full history, and no financial totals (those stay behind login).
    projects = list_all_projects()
    active_projects = [p for p in projects if p.status != "Completed"][:3]
    if not active_projects:
        active_projects = projects[:3]

    for p in active_projects:
        p.actual_spending = get_project_actual_spending(p.id)

    recent_announcements = list_all_announcements()[:3]

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "active_projects": active_projects,
            "recent_announcements": recent_announcements,
        },
    )