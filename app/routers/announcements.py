from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse

from app.core.templates import templates
from app.core.dependencies import require_authenticated, require_role, get_user_role
from app.services.announcement_service import (
    list_all_announcements,
    get_announcement_by_id,
    create_announcement_admin,
)
from app.schemas.announcement import AnnouncementCreate

router = APIRouter(prefix="/announcements", tags=["announcements"])


@router.get("")
def announcements_list(request: Request, user=Depends(require_authenticated)):
    announcements = list_all_announcements()
    is_admin = get_user_role(user) == "admin"

    return templates.TemplateResponse(
        request=request,
        name="announcements/list.html",
        context={
            "announcements": announcements,
            "is_admin": is_admin,
            "base_template": "admin_base.html" if is_admin else "base.html",
        },
    )


@router.get("/new")
def new_announcement_form(request: Request, user=Depends(require_role("admin"))):
    return templates.TemplateResponse(
        request=request,
        name="announcements/create.html",
        context={"error": None},
    )


@router.post("/new")
def new_announcement_submit(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    category: str = Form("general"),
    user=Depends(require_role("admin")),
):
    data = AnnouncementCreate(title=title, content=content, category=category).model_dump()
    published_by = getattr(user, "id", "unknown")
    announcement = create_announcement_admin(data, published_by=published_by)

    return RedirectResponse(url=f"/announcements/{announcement.id}", status_code=303)


@router.get("/{announcement_id}")
def announcement_detail(request: Request, announcement_id: str, user=Depends(require_authenticated)):
    announcement = get_announcement_by_id(announcement_id)
    if announcement is None:
        raise HTTPException(status_code=404, detail="Announcement not found.")

    role = get_user_role(user)

    return templates.TemplateResponse(
        request=request,
        name="announcements/detail.html",
        context={
            "announcement": announcement,
            "base_template": "admin_base.html" if role == "admin" else "base.html",
        },
    )