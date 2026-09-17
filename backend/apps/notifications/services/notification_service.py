from decimal import Decimal

from django.db import IntegrityError, transaction
from django.db.models import Sum

from apps.notifications.models import NotificationLog
from apps.notifications.services.message_service import get_notification_message
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
    # FX-difference settlement needs its own monetary ledger. Do not emit a
    # potentially false alert until that ledger exists.
    return Decimal("0")


def _notification_type(deadline_kind, status):
    if deadline_kind == RegulatoryRule.DeadlineKind.IMPORT_CLEARANCE:
        return status.value  # preserves compatibility with existing logs/UI
    return f"{deadline_kind}_{status.value}"[:50]


def send_notification(*, purchase, today=None):
    if purchase.is_void:
        return False

    deadlines = list(purchase.regulatory_deadlines.all())
    if not deadlines:
        # Legacy records are still supported through CurrencyPurchase.deadline.
        class LegacyDeadline:
            deadline_kind = RegulatoryRule.DeadlineKind.IMPORT_CLEARANCE
            effective_deadline = purchase.deadline
        deadlines = [LegacyDeadline()]

    sent_any = False
    for deadline in deadlines:
        remaining_amount = _remaining_for_deadline(
            purchase=purchase,
            deadline_kind=deadline.deadline_kind,
        )
        status = get_deadline_status(
            deadline=deadline.effective_deadline,
            remaining_amount=remaining_amount,
            today=today,
        )
        if status.value in {"COMPLETED", "NORMAL"}:
            continue

        notification_type = _notification_type(deadline.deadline_kind, status)
        if NotificationLog.objects.filter(
            currency_purchase=purchase,
            notification_type=notification_type,
        ).exists():
            continue

        message = get_notification_message(
            status=status,
            purchase_date=purchase.purchase_date,
            deadline=deadline.effective_deadline,
            purchase_amount=purchase.amount,
            remaining_amount=remaining_amount,
            currency=purchase.currency,
        )
        if not message:
            continue

        try:
            with transaction.atomic():
                NotificationLog.objects.create(
                    currency_purchase=purchase,
                    notification_type=notification_type,
                )
        except IntegrityError:
            continue
        sent_any = True

    return sent_any


def should_send_notification(*, purchase, today=None):
    # Pure preview without writing. Mirrors the conditions used above.
    if purchase.is_void:
        return False
    deadlines = list(purchase.regulatory_deadlines.all())
    if not deadlines:
        return False
    for deadline in deadlines:
        remaining = _remaining_for_deadline(purchase=purchase, deadline_kind=deadline.deadline_kind)
        status = get_deadline_status(deadline=deadline.effective_deadline, remaining_amount=remaining, today=today)
        if status.value in {"COMPLETED", "NORMAL"}:
            continue
        notification_type = _notification_type(deadline.deadline_kind, status)
        if not NotificationLog.objects.filter(currency_purchase=purchase, notification_type=notification_type).exists():
            return True
    return False
