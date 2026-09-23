# app/schemas/assessment.py

from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field


class AssessmentBase(BaseModel):
    assessment_type: Literal["regular", "special"] = "regular"
    description: str
    amount: float = Field(gt=0)
    period_label: Optional[str] = None
    due_date: Optional[str] = None


class AssessmentCreate(AssessmentBase):
    homeowner_id: str


class AssessmentOut(AssessmentBase):
    id: str
    homeowner_id: str
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)