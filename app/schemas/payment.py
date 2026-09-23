# app/schemas/payment.py

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PaymentCreate(BaseModel):
    homeowner_id: str
    assessment_id: Optional[str] = None
    amount: float = Field(gt=0)
    payment_date: str
    payment_method: str = "cash"
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class PaymentOut(BaseModel):
    id: str
    homeowner_id: str
    assessment_id: Optional[str] = None
    amount: float
    payment_date: str
    payment_method: str
    reference_number: Optional[str] = None
    recorded_by: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)