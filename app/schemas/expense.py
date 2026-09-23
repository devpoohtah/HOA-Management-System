# app/schemas/expense.py

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ExpenseCreate(BaseModel):
    category: str
    description: str
    amount: float = Field(gt=0)
    expense_date: str
    vendor: Optional[str] = None
    receipt_url: Optional[str] = None


class ExpenseOut(BaseModel):
    id: str
    category: str
    description: str
    amount: float
    expense_date: str
    vendor: Optional[str] = None
    receipt_url: Optional[str] = None
    recorded_by: Optional[str] = None
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)