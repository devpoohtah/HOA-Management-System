# app/services/financial_summary_service.py

from app.services.dues_service import list_all_assessments_admin
from app.services.payment_service import list_all_payments_admin
from app.services.expense_service import list_all_expenses_admin, get_expense_totals_by_category


def get_community_financial_summary() -> dict:
    """
    Aggregate-only financial summary, safe to show to any logged-in
    user (homeowner or admin) since it contains no per-homeowner
    identifiable data — only sums. Uses admin-client service
    functions internally to pull the full dataset for aggregation,
    but returns totals only, never the underlying rows.
    """
    assessments = list_all_assessments_admin()
    payments = list_all_payments_admin()
    expenses = list_all_expenses_admin()

    expected_collections = sum(a.amount for a in assessments)
    total_outstanding = sum(a.amount for a in assessments if a.status == "UNPAID")
    total_collected = sum(p.amount for p in payments)
    total_expenses = sum(e.amount for e in expenses)
    ending_balance = total_collected - total_expenses

    return {
        "expected_collections": expected_collections,
        "total_collected": total_collected,
        "total_outstanding": total_outstanding,
        "total_expenses": total_expenses,
        "ending_balance": ending_balance,
        "expense_by_category": get_expense_totals_by_category(),
    }