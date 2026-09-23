# app/models/request.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class HOARequest:
    """
    Homeowner-submitted request (certificate, clearance, gate pass,
    facility reservation, other).

    NOTE: class named HOARequest (not Request) to avoid shadowing
    fastapi.Request, which every router in this project imports.

    NOTE: table/column names assumed ("requests": id, homeowner_id,
    request_type, description, status, created_at, updated_at).
    Pending real schema review.

    ASSUMPTION (flagged in response text): same privacy model as
    Complaints — private to the submitting homeowner + admin.
    request_type values and the status lifecycle are both invented
    placeholders; your spec said exact request types "can be
    finalized later" and didn't define statuses for this module.
    """

    id: str
    homeowner_id: str
    request_type: str
    description: str
    status: str = "Submitted"  # Submitted | Processing | Ready for Pickup | Completed
    created_at: Optional[str] = None
    updated_at: Optional[str] = None