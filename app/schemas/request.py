# app/schemas/request.py

from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict

RequestType = Literal["Certificate", "Clearance", "Gate Pass", "Facility Reservation", "Other"]
RequestStatus = Literal["Submitted", "Processing", "Ready for Pickup", "Completed"]


class RequestCreate(BaseModel):
    request_type: RequestType
    description: str


class RequestStatusUpdate(BaseModel):
    status: RequestStatus


class RequestOut(BaseModel):
    id: str
    homeowner_id: str
    request_type: str
    description: str
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)