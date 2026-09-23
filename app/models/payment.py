# app/models/payment.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class Payment:
    """
    Payment = what a homeowner actually paid, against an Assessment.

    NOTE: table/column names assumed ("payments": id, homeowner_id,
    assessment_id, amount, payment_date, payment_method,
    reference_number, recorded_by, notes, created_at). Pending
    real schema review.
    """

    id: str
    homeowner_id: str
    assessment_id: Optional[str]
    amount: float
    payment_date: str
    payment_method: str = "cash"
    reference_number: Optional[str] = None
    recorded_by: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None