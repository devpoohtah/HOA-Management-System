# app/models/assessment.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class Assessment:
    """
    Assessment = what a homeowner is required to pay (regular monthly
    due, special assessment, etc.). Distinct from Payment (what they
    actually paid).

    NOTE: table/column names assumed ("assessments": id, homeowner_id,
    assessment_type, description, amount, period_label, due_date,
    status, created_at, updated_at). Pending real schema review.
    """

    id: str
    homeowner_id: str
    assessment_type: str  # "regular" | "special"
    description: str
    amount: float
    period_label: Optional[str] = None  # e.g. "October 2026"
    due_date: Optional[str] = None
    status: str = "UNPAID"  # "UNPAID" | "PAID"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None