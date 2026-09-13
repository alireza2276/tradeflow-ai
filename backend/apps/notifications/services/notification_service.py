from apps.notifications.models import NotificationLog
from apps.notifications.services.message_service import (
    get_notification_message,
)
from apps.trade_orders.services.balance_service import (
    get_purchase_balance,
)
from apps.trade_orders.services.deadline_service import (
    get_deadline_status,
)

from django.db import IntegrityError, transaction

def should_send_notification(
    *,
    purchase,
    today=None,
):
    if purchase.is_void:
        return False

    balance = get_purchase_balance(
        purchase=purchase,
    )

    remaining_amount = balance["remaining_amount"]

    status = get_deadline_status(
        deadline=purchase.deadline,
        remaining_amount=remaining_amount,
        today=today,
    )

    if status.value in {"COMPLETED", "NORMAL"}:
        return False

    already_sent = NotificationLog.objects.filter(
        currency_purchase=purchase,
        notification_type=status.value,
    ).exists()

    return not already_sent


def send_notification(
    *,
    purchase,
    today=None,
):
    if purchase.is_void:
        return False

    balance = get_purchase_balance(
        purchase=purchase,
    )

    remaining_amount = balance["remaining_amount"]

    status = get_deadline_status(
        deadline=purchase.deadline,
        remaining_amount=remaining_amount,
        today=today,
    )

    if status.value in {"COMPLETED", "NORMAL"}:
        return False

    already_sent = NotificationLog.objects.filter(
        currency_purchase=purchase,
        notification_type=status.value,
    ).exists()

    if already_sent:
        return False

    message = get_notification_message(
        status=status,
        purchase_date=purchase.purchase_date,
        deadline=purchase.deadline,
        purchase_amount=purchase.amount,
        remaining_amount=remaining_amount,
        currency=purchase.currency,
    )

    if not message:
        return False

    # فعلاً ارسال واقعی پیام نداریم.
    # SMS provider در مرحله بعد اینجا وصل می‌شود.

    try:
        with transaction.atomic():
            NotificationLog.objects.create(
                currency_purchase=purchase,
                notification_type=status.value,
            )

    except IntegrityError:
        return False

    return True