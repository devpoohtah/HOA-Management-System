# app/services/document_service.py

from typing import List, Optional

from app.core.supabase_client import get_supabase_admin_client
from app.models.document import Document

TABLE_NAME = "documents"  # NOTE: assumed table name, pending schema confirmation


def _row_to_document(row: dict) -> Document:
    return Document(**row)


def list_all_documents() -> List[Document]:
    """
    Documents have no per-homeowner privacy concern, so this single
    function serves both the admin and homeowner-facing list.
    """
    client = get_supabase_admin_client()
    response = client.table(TABLE_NAME).select("*").order("created_at", desc=True).execute()
    return [_row_to_document(row) for row in response.data]


def get_document_by_id(document_id: str) -> Optional[Document]:
    client = get_supabase_admin_client()
    response = (
        client.table(TABLE_NAME).select("*").eq("id", document_id).limit(1).execute()
    )
    if not response.data:
        return None
    return _row_to_document(response.data[0])


def create_document_admin(data: dict, uploaded_by: str) -> Document:
    """Admin-only: publish a new HOA document reference."""
    document_data = {**data, "uploaded_by": uploaded_by}
    client = get_supabase_admin_client()
    response = client.table(TABLE_NAME).insert(document_data).execute()
    return _row_to_document(response.data[0])