# app/models/project.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class Project:
    """
    HOA project/maintenance initiative (road repairs, street lighting,
    drainage, community improvements, etc.).

    NOTE: table/column names assumed ("projects": id, name,
    description, budget, status, start_date, completion_date,
    created_at, updated_at). Pending real schema review.

    ASSUMPTION (flagged in response text): actual_spending is NOT a
    stored column — it's computed on read from linked expenses
    (expenses.project_id) rather than manually entered.
    """

    id: str
    name: str
    description: str
    budget: float
    status: str = "Planned"  # Planned | In Progress | Completed | On Hold
    start_date: Optional[str] = None
    completion_date: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None