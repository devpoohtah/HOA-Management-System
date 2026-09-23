# app/schemas/complaint.py

from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict

ComplaintStatus = Literal["Submitted", "Under Review", "In Progress", "Resolved"]
ComplaintCategory = Literal[
    "Security", "Garbage", "Roads", "Drainage", "Noise", "Water", "Street Lights", "Other"
]


class ComplaintCreate(BaseModel):
    category: ComplaintCategory
    description: str


class ComplaintStatusUpdate(BaseModel):
    status: ComplaintStatus


class ComplaintOut(BaseModel):
    id: str
    homeowner_id: str
    category: str
    description: str
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)