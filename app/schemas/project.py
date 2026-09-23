# app/schemas/project.py

from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field

ProjectStatus = Literal["Planned", "In Progress", "Completed", "On Hold"]


class ProjectCreate(BaseModel):
    name: str
    description: str
    budget: float = Field(ge=0)
    start_date: Optional[str] = None
    completion_date: Optional[str] = None


class ProjectStatusUpdate(BaseModel):
    status: ProjectStatus


class ProjectOut(BaseModel):
    id: str
    name: str
    description: str
    budget: float
    status: str
    start_date: Optional[str] = None
    completion_date: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)