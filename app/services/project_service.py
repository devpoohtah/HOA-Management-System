# app/services/project_service.py

from typing import List, Optional

from app.core.supabase_client import get_supabase_admin_client
from app.models.project import Project
from app.services.expense_service import list_expenses_by_project_admin

TABLE_NAME = "projects"  # NOTE: assumed table name, pending schema confirmation


def _row_to_project(row: dict) -> Project:
    return Project(**row)


def list_all_projects() -> List[Project]:
    """
    Projects have no per-homeowner privacy concern (supports
    financial transparency), so this single function serves both
    the admin and homeowner-facing views.
    """
    client = get_supabase_admin_client()
    response = client.table(TABLE_NAME).select("*").order("start_date", desc=True).execute()
    return [_row_to_project(row) for row in response.data]


def get_project_by_id(project_id: str) -> Optional[Project]:
    client = get_supabase_admin_client()
    response = (
        client.table(TABLE_NAME).select("*").eq("id", project_id).limit(1).execute()
    )
    if not response.data:
        return None
    return _row_to_project(response.data[0])


def get_project_actual_spending(project_id: str) -> float:
    """
    Computes actual spending from expenses linked to this project,
    rather than reading a stored/manually-entered number. See the
    ASSUMPTION note on app.models.project.Project.
    """
    expenses = list_expenses_by_project_admin(project_id)
    return sum(e.amount for e in expenses)


def create_project_admin(data: dict) -> Project:
    """Admin-only: create a new project."""
    project_data = {**data, "status": "Planned"}
    client = get_supabase_admin_client()
    response = client.table(TABLE_NAME).insert(project_data).execute()
    return _row_to_project(response.data[0])


def update_project_status_admin(project_id: str, status: str) -> Optional[Project]:
    """Admin-only: move a project through its status lifecycle."""
    client = get_supabase_admin_client()
    response = (
        client.table(TABLE_NAME)
        .update({"status": status})
        .eq("id", project_id)
        .execute()
    )
    if not response.data:
        return None
    return _row_to_project(response.data[0])