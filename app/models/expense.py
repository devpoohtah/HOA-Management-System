# app/models/expense.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class Expense:
    """
    Expense = HOA money going out.

    NOTE: table/column names assumed ("expenses": id, category,
    description, amount, expense_date, vendor, receipt_url,
    recorded_by, created_at). No approval-status field — an
    approval workflow was explicitly not confirmed, so none is
    assumed here. Pending real schema review.
    """

    id: str
    category: str
    description: str
    amount: float
    expense_date: str
    vendor: Optional[str] = None
    receipt_url: Optional[str] = None
    recorded_by: Optional[str] = None
    created_at: Optional[str] = None