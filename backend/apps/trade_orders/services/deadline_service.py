from datetime import date

from dateutil.relativedelta import relativedelta


DEFAULT_COMMERCIAL_DEADLINE_MONTHS = 6
DEFAULT_PRODUCTION_DEADLINE_MONTHS = 9


def resolve_shipment_deadline_months(
    *,
    activity_type: str,
    configured_months: int | None,
) -> int:
    """Resolve the deadline configured for the registration order.

    CBI Part One rules can vary by goods/source/table. Therefore the
    registration-order value wins. The 6/9 month values are only a
    backward-compatible baseline for records not yet classified.
    """
    if configured_months is not None:
        if configured_months <= 0:
            raise ValueError("Shipment deadline months must be positive.")
        return configured_months

    if activity_type == "COMMERCIAL":
        return DEFAULT_COMMERCIAL_DEADLINE_MONTHS
    if activity_type == "PRODUCTION":
        return DEFAULT_PRODUCTION_DEADLINE_MONTHS
    raise ValueError(f"Unsupported activity type: {activity_type}")


def calculate_purchase_deadline(
    *,
    remittance_date: date | None = None,
    activity_type: str | None = None,
    configured_months: int | None = None,
    # Backward-compatible aliases for existing tests/callers.
    purchase_date: date | None = None,
    company_type: str | None = None,
) -> date:
    basis_date = remittance_date or purchase_date
    resolved_activity_type = activity_type or company_type

    if basis_date is None:
        raise ValueError("Remittance date is required.")
    if not resolved_activity_type:
        raise ValueError("Activity type is required.")

    months = resolve_shipment_deadline_months(
        activity_type=resolved_activity_type,
        configured_months=configured_months,
    )
    return basis_date + relativedelta(months=months)

from enum import Enum


class DeadlineStatus(str, Enum):
    COMPLETED = "COMPLETED"
    NINETY_DAYS = "NINETY_DAYS"
    SIXTY_DAYS = "SIXTY_DAYS"
    THIRTY_DAYS = "THIRTY_DAYS"
    TWENTY_DAYS = "TWENTY_DAYS"
    TEN_DAYS = "TEN_DAYS"
    FIVE_DAYS = "FIVE_DAYS"
    LAST_DAY = "LAST_DAY"
    OVERDUE = "OVERDUE"
    NORMAL = "NORMAL"


NOTIFICATION_DAYS = {
    90: DeadlineStatus.NINETY_DAYS,
    60: DeadlineStatus.SIXTY_DAYS,
    30: DeadlineStatus.THIRTY_DAYS,
    20: DeadlineStatus.TWENTY_DAYS,
    10: DeadlineStatus.TEN_DAYS,
    5: DeadlineStatus.FIVE_DAYS,
    0: DeadlineStatus.LAST_DAY,
}


def get_deadline_status(
    *,
    deadline: date,
    remaining_amount,
    today: date | None = None,
) -> DeadlineStatus:

    if today is None:
        today = date.today()

    if remaining_amount <= 0:
        return DeadlineStatus.COMPLETED

    days_remaining = (deadline - today).days

    if days_remaining < 0:
        return DeadlineStatus.OVERDUE

    return NOTIFICATION_DAYS.get(
        days_remaining,
        DeadlineStatus.NORMAL,
    )