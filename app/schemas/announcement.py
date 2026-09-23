# app/schemas/announcement.py

from typing import Optional
from pydantic import BaseModel, ConfigDict


class AnnouncementCreate(BaseModel):
    title: str
    content: str
    category: str = "general"


class AnnouncementOut(BaseModel):
    id: str
    title: str
    content: str
    category: str
    published_by: Optional[str] = None
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)