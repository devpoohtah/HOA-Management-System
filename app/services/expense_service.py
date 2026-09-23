# app/services/expense_service.py

from typing import List

from app.core.supabase_client import get_supabase_admin_client
from app.models.expense import Expense

TABLE_NAME = "expenses"  # NOTE: assumed table name, pending schema confirmation


def _row_to_expense(row: dict) -> Expense:
    return Expense(**row)


def list_all_expenses_admin() -> List[Expense]:
    """
    Admin-only: full expense ledger, most recent first.
    Caller must already be authorized (require_role) — this function
    performs no authorization check itself.
    """
    client = get_supabase_admin_client()
    response = client.table(TABLE_NAME).select("*").order("expense_date", desc=True).execute()
    return [_row_to_expense(row) for row in response.data]


def list_all_expenses_public() -> List[Expense]:
    """
    Read-only, aggregate-safe listing used for the homeowner-facing
    transparency view. Kept as a separate function from the admin
    listing in case per-expense visibility rules are ever introduced.
    """
    return list_all_expenses_admin()


def list_expenses_by_project_admin(project_id: str) -> List[Expense]:
    """
    Admin-only: expenses linked to a specific project, used to
    compute a project's actual spending total.
    """
    client = get_supabase_admin_client()
    response = (
        client.table(TABLE_NAME)
        .select("*")
        .eq("project_id", project_id)
        .order("expense_date", desc=True)
        .execute()
    )
    return [_row_to_expense(row) for row in response.data]


def get_expense_totals_by_category() -> dict:
    """
    Aggregates total spending per category, for the financial
    transparency summary (dashboard, homeowner summary view, etc.).
    """
    expenses = list_all_expenses_admin()
    totals: dict = {}
    for e in expenses:
        totals[e.category] = totals.get(e.category, 0) + e.amount
    return totals


def create_expense_admin(data: dict, recorded_by: str) -> Expense:
    """Admin-only: record a new expense."""
    expense_data = {**data, "recorded_by": recorded_by}
    client = get_supabase_admin_client()
    response = client.table(TABLE_NAME).insert(expense_data).execute()
    return _row_to_expense(response.data[0])