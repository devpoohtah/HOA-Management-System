from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from typing import List, Optional

from app.core.templates import templates
from app.core.dependencies import require_authenticated, require_role, get_user_role
from app.services.meeting_service import (
    list_all_meetings,
    get_meeting_by_id,
    create_meeting_admin,
    update_meeting_minutes_admin,
)
from app.services.homeowner_service import list_all_homeowners_admin
from app.schemas.meeting import MeetingCreate, MeetingMinutesUpdate

router = APIRouter(prefix="/meetings", tags=["meetings"])

def _split_attendees(attendees_text, homeowners):
    """
    Split the saved attendees text into (names matching a homeowner, guest text)
    so the minutes form can pre-check boxes and pre-fill the guests box.
    """
    names = [n.strip() for n in (attendees_text or "").split(",") if n.strip()]
    known = {h.full_name for h in homeowners}
    selected = [n for n in names if n in known]
    guests = ", ".join(n for n in names if n not in known)
    return selected, guests

@router.get("")
def meetings_list(request: Request, user=Depends(require_authenticated)):
    meetings = list_all_meetings()
    role = get_user_role(user)

    return templates.TemplateResponse(
        request=request,
        name="meetings/list.html",
        context={
            "meetings": meetings,
            "base_template": "admin_base.html" if role == "admin" else "base.html",
        },
    )


@router.get("/new")
def new_meeting_form(request: Request, user=Depends(require_role("admin"))):
    return templates.TemplateResponse(
        request=request,
        name="meetings/new.html",
        context={"error": None},
    )


@router.post("/new")
def new_meeting_submit(
    request: Request,
    title: str = Form(...),
    meeting_date: str = Form(...),
    meeting_time: Optional[str] = Form(None),
    location: str = Form(...),
    agenda: str = Form(...),
    user=Depends(require_role("admin")),
):
    data = MeetingCreate(
        title=title,
        meeting_date=meeting_date,
        meeting_time=meeting_time,
        location=location,
        agenda=agenda,
    ).model_dump()

    meeting = create_meeting_admin(data)
    return RedirectResponse(url=f"/meetings/{meeting.id}", status_code=303)


@router.get("/{meeting_id}")
def meeting_detail(request: Request, meeting_id: str, user=Depends(require_authenticated)):
    meeting = get_meeting_by_id(meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found.")

    is_admin_view = get_user_role(user) == "admin"

    picker_homeowners = []
    selected_names = []
    guest_text = ""
    if is_admin_view:
        all_homeowners = list_all_homeowners_admin()
        picker_homeowners = sorted(
            (h for h in all_homeowners if getattr(h, "is_active", True)),
            key=lambda h: h.full_name,
        )
        selected_names, guest_text = _split_attendees(meeting.attendees, all_homeowners)

    return templates.TemplateResponse(
        request=request,
        name="meetings/detail.html",
        context={
            "meeting": meeting,
            "is_admin_view": is_admin_view,
            "homeowners": picker_homeowners,
            "selected_names": selected_names,
            "guest_text": guest_text,
            "base_template": "admin_base.html" if is_admin_view else "base.html",
        },
    )


@router.post("/{meeting_id}/minutes")
def update_meeting_minutes(
    request: Request,
    meeting_id: str,
    minutes: str = Form(...),
    decisions: Optional[str] = Form(None),
    attendee_ids: List[str] = Form([]),
    guests: Optional[str] = Form(None),
    user=Depends(require_role("admin")),
):
    names_by_id = {h.id: h.full_name for h in list_all_homeowners_admin()}
    attendee_names = [names_by_id[i] for i in attendee_ids if i in names_by_id]
    guest_names = [g.strip() for g in (guests or "").split(",") if g.strip()]
    attendees = ", ".join(attendee_names + guest_names) or None

    data = MeetingMinutesUpdate(minutes=minutes, decisions=decisions, attendees=attendees).model_dump()
    update_meeting_minutes_admin(meeting_id, data)
    return RedirectResponse(url=f"/meetings/{meeting_id}", status_code=303)