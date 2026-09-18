from apps.notifications.services.notification_service import send_notification
from apps.trade_orders.models import CurrencyPurchase
from apps.trade_orders.services.compliance_service import refresh_obligation_status


def process_deadline_notifications(*, today=None):
    purchases = CurrencyPurchase.objects.filter(
        registration_order__is_active=True,
        is_void=False,
    ).exclude(
        obligation_status=CurrencyPurchase.ObligationStatus.SETTLED,
    ).select_related("registration_order", "registration_order__company").prefetch_related("regulatory_deadlines")

    processed_count = 0
    sent_count = 0
    for purchase in purchases:
        purchase = refresh_obligation_status(purchase)
        if purchase.obligation_status == CurrencyPurchase.ObligationStatus.SETTLED:
            continue
        sent = send_notification(purchase=purchase, today=today)
        processed_count += 1
        if sent:
            sent_count += 1
    return {"processed_count": processed_count, "sent_count": sent_count}
