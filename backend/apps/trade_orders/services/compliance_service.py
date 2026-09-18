from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.trade_orders.models import CurrencyPurchase, CustomsClearance, DeadlineExtension, RegulatoryDeadline, RegulatoryRule
from apps.trade_orders.services.validation import get_total_shipment_amount


def get_clearance_total(purchase):
    return purchase.customs_clearances.exclude(status=CustomsClearance.Status.REJECTED).aggregate(total=Sum("amount"))["total"] or Decimal("0")


def derive_obligation_status(purchase, *, today=None):
    today = today or timezone.localdate()
    shipped = get_total_shipment_amount(purchase)
    cleared = get_clearance_total(purchase)
    if purchase.obligation_settled_at:
        return CurrencyPurchase.ObligationStatus.SETTLED
    if purchase.deadline < today and cleared < purchase.amount:
        return CurrencyPurchase.ObligationStatus.OVERDUE
    if cleared >= purchase.amount:
        return CurrencyPurchase.ObligationStatus.CLEARED
    if cleared > 0:
        return CurrencyPurchase.ObligationStatus.PARTIALLY_CLEARED
    if shipped >= purchase.amount:
        return CurrencyPurchase.ObligationStatus.CLEARANCE_PENDING
    return CurrencyPurchase.ObligationStatus.OPEN


@transaction.atomic
def refresh_obligation_status(purchase):
    locked = CurrencyPurchase.objects.select_for_update().get(pk=purchase.pk)
    status = derive_obligation_status(locked)
    if locked.obligation_status != status:
        locked.obligation_status = status
        locked.save(update_fields=("obligation_status", "updated_at"))
    return locked


@transaction.atomic
def extend_deadline(*, purchase, new_deadline, reason, approved_by, reference="", deadline_kind=RegulatoryRule.DeadlineKind.IMPORT_CLEARANCE):
    locked = CurrencyPurchase.objects.select_for_update().get(pk=purchase.pk)
    if locked.is_void:
        raise ValidationError("Voided currency purchases cannot be extended.")
    if not reason.strip():
        raise ValidationError("An extension reason is required.")

    regulatory_deadline = (
        RegulatoryDeadline.objects.select_for_update()
        .filter(currency_purchase=locked, deadline_kind=deadline_kind)
        .first()
    )
    if regulatory_deadline is None:
        raise ValidationError(f"No {deadline_kind} deadline exists for this purchase.")
    if new_deadline <= regulatory_deadline.effective_deadline:
        raise ValidationError("The extended deadline must be later than the current effective deadline.")

    previous = regulatory_deadline.effective_deadline
    event = DeadlineExtension.objects.create(
        currency_purchase=locked,
        regulatory_deadline=regulatory_deadline,
        previous_deadline=previous,
        new_deadline=new_deadline,
        reason=reason.strip(),
        reference=reference.strip(),
        approved_by=approved_by,
    )
    regulatory_deadline.effective_deadline = new_deadline
    regulatory_deadline.save(update_fields=("effective_deadline", "updated_at"))

    # Compatibility projection: CurrencyPurchase.deadline remains the effective
    # IMPORT_CLEARANCE deadline used by the existing dashboard/notifications.
    if deadline_kind == RegulatoryRule.DeadlineKind.IMPORT_CLEARANCE:
        locked.deadline = new_deadline
        locked.deadline_extension_reason = reason.strip()
        locked.deadline_extension_reference = reference.strip()
        locked.save(update_fields=("deadline", "deadline_extension_reason", "deadline_extension_reference", "updated_at"))
    return event


@transaction.atomic
def mark_obligation_settled(*, purchase, settled=True, actor=None, reason="", reference=""):
    locked = CurrencyPurchase.objects.select_for_update().get(pk=purchase.pk)
    if locked.is_void:
        raise ValidationError("Voided currency purchases cannot be settled or reopened.")

    if settled:
        if locked.obligation_settled_at:
            raise ValidationError("FX obligation is already settled.")
        if get_clearance_total(locked) < locked.amount:
            raise ValidationError("FX obligation cannot be marked settled before the purchase amount is cleared.")
        if not reason.strip():
            raise ValidationError("A settlement reason is required.")
        locked.obligation_settled_at = timezone.now()
        locked.obligation_settled_by = actor
        locked.obligation_settlement_reason = reason.strip()
        locked.obligation_settlement_reference = reference.strip()
        locked.obligation_status = CurrencyPurchase.ObligationStatus.SETTLED
    else:
        if not locked.obligation_settled_at:
            raise ValidationError("FX obligation is not settled.")
        if not reason.strip():
            raise ValidationError("A reopen reason is required.")
        locked.obligation_settled_at = None
        locked.obligation_settled_by = None
        locked.obligation_settlement_reason = f"REOPENED: {reason.strip()}"
        locked.obligation_settlement_reference = reference.strip()
        locked.obligation_status = derive_obligation_status(locked)

    locked.save(update_fields=(
        "obligation_settled_at", "obligation_settled_by",
        "obligation_settlement_reason", "obligation_settlement_reference",
        "obligation_status", "updated_at",
    ))
    return locked
