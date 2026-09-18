from decimal import Decimal

from apps.common.services.date_service import format_dual_date
from apps.trade_orders.models import RegulatoryRule
from apps.trade_orders.services.deadline_service import DeadlineStatus


def _deadline_label(deadline_kind):
    labels = {
        RegulatoryRule.DeadlineKind.IMPORT_CLEARANCE: "مهلت ورود/ترخیص",
        RegulatoryRule.DeadlineKind.SHIPPING_DOCUMENTS: "مهلت اسناد حمل",
        RegulatoryRule.DeadlineKind.FX_DIFFERENCE: "مهلت مابه‌التفاوت ارزی",
    }
    return labels.get(deadline_kind, "مهلت پرونده")


def get_notification_message(
    *, status, purchase_date, deadline, purchase_amount: Decimal,
    remaining_amount: Decimal, currency: str, deadline_kind="",
):
    messages = {
        DeadlineStatus.NINETY_DAYS: "90 روز تا سررسید باقی مانده است.",
        DeadlineStatus.SIXTY_DAYS: "60 روز تا سررسید باقی مانده است.",
        DeadlineStatus.THIRTY_DAYS: "30 روز تا سررسید باقی مانده است.",
        DeadlineStatus.TWENTY_DAYS: "20 روز تا سررسید باقی مانده است.",
        DeadlineStatus.TEN_DAYS: "10 روز تا سررسید باقی مانده است.",
        DeadlineStatus.FIVE_DAYS: "5 روز تا سررسید باقی مانده است.",
        DeadlineStatus.LAST_DAY: "امروز آخرین روز مهلت است.",
        DeadlineStatus.OVERDUE: "مهلت پرونده به پایان رسیده است.",
    }
    message = messages.get(status)
    if not message:
        return None
    return (
        f"TradeFlowAI\n{message}\n"
        f"نوع مهلت: {_deadline_label(deadline_kind)}\n"
        f"مبلغ خرید ارز: {purchase_amount} {currency}\n"
        f"مبلغ باقی‌مانده: {remaining_amount} {currency}\n"
        f"تاریخ خرید: {format_dual_date(purchase_date)}\n"
        f"سررسید مؤثر: {format_dual_date(deadline)}"
    )
