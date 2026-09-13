from apps.notifications.services.notification_service import (
    send_notification,
)
from apps.trade_orders.models import CurrencyPurchase


def process_deadline_notifications(*, today=None):
    purchases = CurrencyPurchase.objects.filter(
        registration_order__is_active=True,
        is_void=False,
    )

    processed_count = 0
    sent_count = 0

    for purchase in purchases:
        sent = send_notification(
            purchase=purchase,
            today=today,
        )

        processed_count += 1

        if sent:
            sent_count += 1

    return {
        "processed_count": processed_count,
        "sent_count": sent_count,
    }