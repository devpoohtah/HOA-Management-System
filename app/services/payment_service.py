# app/services/payment_service.py

from typing import List

from app.core.supabase_client import get_supabase_admin_client, get_user_scoped_client
from app.models.payment import Payment
from app.services.dues_service import get_assessment_by_id_admin, mark_assessment_paid_admin

TABLE_NAME = "payments"  # NOTE: assumed table name, pending schema confirmation


def _row_to_payment(row: dict) -> Payment:
    return Payment(**row)


def list_all_payments_admin() -> List[Payment]:
    """Admin-only: every payment, most recent first."""
    client = get_supabase_admin_client()
    response = client.table(TABLE_NAME).select("*").order("payment_date", desc=True).execute()
    return [_row_to_payment(row) for row in response.data]


def list_own_payments(access_token: str, homeowner_id: str) -> List[Payment]:
    """Homeowner self-view: own payment history only."""
    client = get_user_scoped_client(access_token)
    response = (
        client.table(TABLE_NAME)
        .select("*")
        .eq("homeowner_id", homeowner_id)
        .order("payment_date", desc=True)
        .execute()
    )
    return [_row_to_payment(row) for row in response.data]


def record_payment_admin(data: dict, recorded_by: str) -> Payment:
    """
    Admin/secretary-only: digitizes a cash payment already collected
    in person. Does NOT replace the physical receipt.

    ASSUMPTION (flagged): a payment fully closes its linked assessment
    regardless of amount — no partial-payment/remaining-balance
    tracking exists yet. See module-level note in the response this
    was generated in.
    """
    payment_data = {**data, "recorded_by": recorded_by}

    client = get_supabase_admin_client()
    response = client.table(TABLE_NAME).insert(payment_data).execute()
    payment = _row_to_payment(response.data[0])

    if payment.assessment_id:
        assessment = get_assessment_by_id_admin(payment.assessment_id)
        if assessment is not None:
            mark_assessment_paid_admin(payment.assessment_id)

    return payment  