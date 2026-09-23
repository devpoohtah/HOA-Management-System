# app/models/complaint.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class Complaint:
    """
    Homeowner-submitted complaint/concern.

    NOTE: table/column names assumed ("complaints": id, homeowner_id,
    category, description, status, created_at, updated_at). Pending
    real schema review.

    ASSUMPTION (flagged in response text): complaints are private to
    the submitting homeowner + admin, not visible to other
    homeowners. Confirm this matches intent.
    """

    id: str
    homeowner_id: str
    category: str
    description: str
    status: str = "Submitted"  # Submitted | Under Review | In Progress | Resolved
    created_at: Optional[str] = None
    updated_at: Optional[str] = None