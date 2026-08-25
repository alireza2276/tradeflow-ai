from datetime import date

from dateutil.relativedelta import relativedelta


COMMERCIAL_DEADLINE_MONTHS = 6
PRODUCTION_DEADLINE_MONTHS = 9


def calculate_purchase_deadline(
    *,
    purchase_date: date,
    company_type: str,
) -> date:
    if company_type == "COMMERCIAL":
        months = COMMERCIAL_DEADLINE_MONTHS

    elif company_type == "PRODUCTION":
        months = PRODUCTION_DEADLINE_MONTHS

    else:
        raise ValueError(
            f"Unsupported company type: {company_type}"
        )

    return purchase_date + relativedelta(months=months)

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