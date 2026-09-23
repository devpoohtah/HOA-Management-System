# app/models/document.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class Document:
    """
    HOA document (bylaws, rules, meeting minutes, financial reports,
    annual reports, resolutions, notices, project documents).

    NOTE: table/column names assumed ("documents": id, title,
    category, file_url, uploaded_by, created_at). Pending real
    schema review.

    file_url is a plain link/reference, NOT a Supabase Storage
    upload — Storage was explicitly marked optional and not to be
    added just because it exists, so this mirrors the same approach
    used for expense receipts in Phase 4.
    """

    id: str
    title: str
    category: str
    file_url: Optional[str] = None
    uploaded_by: Optional[str] = None
    created_at: Optional[str] = None