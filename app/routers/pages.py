# app/routers/pages.py

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.core.templates import templates
from app.core.security import get_current_user

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

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={},
    )