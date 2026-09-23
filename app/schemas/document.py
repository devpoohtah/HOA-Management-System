# app/schemas/document.py

from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict

DocumentCategory = Literal[
    "Bylaws",
    "Rules and Regulations",
    "Meeting Minutes",
    "Financial Reports",
    "Annual Reports",
    "Resolutions",
    "Notices",
    "Project Documents",
    "Other",
]


class DocumentCreate(BaseModel):
    title: str
    category: DocumentCategory
    file_url: Optional[str] = None


class DocumentOut(BaseModel):
    id: str
    title: str
    category: str
    file_url: Optional[str] = None
    uploaded_by: Optional[str] = None
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)