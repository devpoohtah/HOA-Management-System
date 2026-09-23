# app/schemas/meeting.py

from typing import Optional
from pydantic import BaseModel, ConfigDict


class MeetingCreate(BaseModel):
    title: str
    meeting_date: str
    meeting_time: Optional[str] = None
    location: str
    agenda: str


class MeetingMinutesUpdate(BaseModel):
    minutes: str
    decisions: Optional[str] = None
    attendees: Optional[str] = None


class MeetingOut(BaseModel):
    id: str
    title: str
    meeting_date: str
    meeting_time: Optional[str] = None
    location: str
    agenda: str
    minutes: Optional[str] = None
    decisions: Optional[str] = None
    attendees: Optional[str] = None
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)