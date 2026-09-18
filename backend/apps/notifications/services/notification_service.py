from decimal import Decimal

from django.db import IntegrityError, transaction
from django.db.models import Q, Sum
from django.utils import timezone

from apps.notifications.models import NotificationDelivery, NotificationLog
from apps.notifications.services.message_service import get_notification_message
from apps.notifications.services.recipient_service import list_recipients_for_purchase
from apps.notifications.services.sms_service import get_sms_provider
from apps.trade_orders.models import CustomsClearance, RegulatoryRule
from apps.trade_orders.services.deadline_service import get_deadline_status
from apps.trade_orders.services.validation import get_total_shipment_amount


def _remaining_for_deadline(*, purchase, deadline_kind):
    if deadline_kind == RegulatoryRule.DeadlineKind.SHIPPING_DOCUMENTS:
        return max(purchase.amount - get_total_shipment_amount(purchase), Decimal("0"))
    if deadline_kind == RegulatoryRule.DeadlineKind.IMPORT_CLEARANCE:
        cleared = purchase.customs_clearances.exclude(
            status=CustomsClearance.Status.REJECTED
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")
        return max(purchase.amount - cleared, Decimal("0"))
    # Dedicated FX-difference ledger is not implemented yet. Do not invent a balance.
    return Decimal("0")


def _notification_type(deadline_kind, status):
    if deadline_kind == RegulatoryRule.DeadlineKind.IMPORT_CLEARANCE:
        return status.value
    return f"{deadline_kind}_{status.value}"[:80]



def _event_exists(*, purchase, notification_type, deadline_kind, deadline_date):
    # Also recognizes legacy V0 rows created before deadline dimensions existed.
    return NotificationLog.objects.filter(
        currency_purchase=purchase,
        notification_type=notification_type,
    ).filter(
        Q(deadline_kind=deadline_kind, deadline_date=deadline_date)
        | Q(deadline_kind="", deadline_date__isnull=True)
    ).exists()


def _create_deliveries(*, notification, purchase):
    recipients = list(list_recipients_for_purchase(purchase=purchase))
    provider = get_sms_provider()

    for recipient in recipients:
        if recipient.in_app_enabled:
            NotificationDelivery.objects.get_or_create(
                notification=notification,
                recipient=recipient,
                channel=NotificationDelivery.Channel.IN_APP,
                defaults={
                    "destination": recipient.display_name,
                    "status": NotificationDelivery.Status.SENT,
                    "provider": "TRADEFLOWAI",
                    "attempted_at": timezone.now(),
                    "sent_at": timezone.now(),
                },
            )

        if not recipient.sms_enabled or not recipient.phone_number:
            continue

        delivery, created = NotificationDelivery.objects.get_or_create(
            notification=notification,
            recipient=recipient,
            channel=NotificationDelivery.Channel.SMS,
            defaults={
                "destination": recipient.phone_number,
                "status": NotificationDelivery.Status.PENDING,
            },
        )
        if not created or delivery.status == NotificationDelivery.Status.SENT:
            continue

        attempted_at = timezone.now()
        result = provider.send(phone_number=recipient.phone_number, message=notification.message)
        delivery.attempted_at = attempted_at
        delivery.provider = result.provider
        delivery.provider_message_id = result.message_id
        delivery.error_message = result.error
        if result.success:
            delivery.status = NotificationDelivery.Status.SENT
            delivery.sent_at = timezone.now()
        else:
            # DISABLED is expected in V1 and is auditable, not silently ignored.
            delivery.status = NotificationDelivery.Status.SKIPPED if result.provider == "DISABLED" else NotificationDelivery.Status.FAILED
        delivery.save(update_fields=[
            "attempted_at", "provider", "provider_message_id", "error_message", "status", "sent_at"
        ])


def send_notification(*, purchase, today=None):
    if purchase.is_void or purchase.obligation_status == purchase.ObligationStatus.SETTLED:
        return False

    deadlines = list(purchase.regulatory_deadlines.all())
    if not deadlines:
        class LegacyDeadline:
            deadline_kind = RegulatoryRule.DeadlineKind.IMPORT_CLEARANCE
            effective_deadline = purchase.deadline
        deadlines = [LegacyDeadline()]

    sent_any = False
    for deadline in deadlines:
        remaining_amount = _remaining_for_deadline(purchase=purchase, deadline_kind=deadline.deadline_kind)
        status = get_deadline_status(
            deadline=deadline.effective_deadline,
            remaining_amount=remaining_amount,
            today=today,
        )
        if status.value in {"COMPLETED", "NORMAL"}:
            continue

        notification_type = _notification_type(deadline.deadline_kind, status)
        message = get_notification_message(
            status=status,
            purchase_date=purchase.purchase_date,
            deadline=deadline.effective_deadline,
            purchase_amount=purchase.amount,
            remaining_amount=remaining_amount,
            currency=purchase.currency,
            deadline_kind=deadline.deadline_kind,
        )
        if not message:
            continue

        try:
            with transaction.atomic():
                notification, created = NotificationLog.objects.get_or_create(
                    currency_purchase=purchase,
                    notification_type=notification_type,
                    deadline_kind=deadline.deadline_kind,
                    deadline_date=deadline.effective_deadline,
                    defaults={"message": message},
                )
        except IntegrityError:
            continue

        if not created:
            continue
        _create_deliveries(notification=notification, purchase=purchase)
        sent_any = True

    return sent_any


def should_send_notification(*, purchase, today=None):
    if purchase.is_void or purchase.obligation_status == purchase.ObligationStatus.SETTLED:
        return False
    deadlines = list(purchase.regulatory_deadlines.all())
    if not deadlines:
        return False
    for deadline in deadlines:
        remaining = _remaining_for_deadline(purchase=purchase, deadline_kind=deadline.deadline_kind)
        status = get_deadline_status(
            deadline=deadline.effective_deadline,
            remaining_amount=remaining,
            today=today,
        )
        if status.value in {"COMPLETED", "NORMAL"}:
            continue
        notification_type = _notification_type(deadline.deadline_kind, status)
        exists = _event_exists(
            purchase=purchase,
            notification_type=notification_type,
            deadline_kind=deadline.deadline_kind,
            deadline_date=deadline.effective_deadline,
        )
        if not exists:
            return True
    return False
