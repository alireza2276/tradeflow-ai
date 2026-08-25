from decimal import Decimal

from apps.common.services.date_service import format_dual_date
from apps.trade_orders.services.deadline_service import DeadlineStatus


def get_notification_message(
    *,
    status,
    purchase_date,
    deadline,
    purchase_amount: Decimal,
    remaining_amount: Decimal,
    currency: str,
):
    messages = {
        DeadlineStatus.NINETY_DAYS: (
            "90 روز تا پایان مهلت ارائه اسناد حمل شما باقی مانده است."
        ),
        DeadlineStatus.SIXTY_DAYS: (
            "60 روز تا پایان مهلت ارائه اسناد حمل شما باقی مانده است."
        ),
        DeadlineStatus.THIRTY_DAYS: (
            "30 روز تا پایان مهلت ارائه اسناد حمل شما باقی مانده است."
        ),
        DeadlineStatus.TWENTY_DAYS: (
            "20 روز تا پایان مهلت ارائه اسناد حمل شما باقی مانده است."
        ),
        DeadlineStatus.TEN_DAYS: (
            "10 روز تا پایان مهلت ارائه اسناد حمل شما باقی مانده است."
        ),
        DeadlineStatus.FIVE_DAYS: (
            "5 روز تا پایان مهلت ارائه اسناد حمل شما باقی مانده است."
        ),
        DeadlineStatus.LAST_DAY: (
            "امروز آخرین مهلت ارائه اسناد حمل شما است."
        ),
        DeadlineStatus.OVERDUE: (
            "مهلت ارائه اسناد حمل شما به پایان رسیده است."
        ),
    }

    message = messages.get(status)

    if not message:
        return None

    return (
        f"{message}\n\n"
        f"مبلغ خرید ارز: {purchase_amount} {currency}\n"
        f"مبلغ باقی‌مانده: {remaining_amount} {currency}\n\n"
        f"تاریخ خرید: {format_dual_date(purchase_date)}\n"
        f"مهلت ارائه اسناد: {format_dual_date(deadline)}"
    )