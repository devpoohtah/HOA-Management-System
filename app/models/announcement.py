# app/models/announcement.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class Announcement:
    """
    HOA-published announcement (meetings, water interruptions, road
    maintenance, security notices, dues reminders, community notices,
    etc.).

    NOTE: table/column names assumed ("announcements": id, title,
    content, category, published_by, created_at). Pending real
    schema review.
    """

    id: str
    title: str
    content: str
    category: str = "general"
    published_by: Optional[str] = None
    created_at: Optional[str] = None