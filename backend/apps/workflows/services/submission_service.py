from datetime import date
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.trade_orders.models import RegistrationOrder
from apps.trade_orders.services.validation import (
    validate_purchase_amount,
)
from apps.workflows.models import ApprovalRequest


CURRENCY_PURCHASE_TARGET = "currency_purchase"


def _normalize_decimal(value) -> Decimal:
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError(
            "Invalid purchase amount."
        )

    if not decimal_value.is_finite():
        raise ValidationError(
            "Invalid purchase amount."
        )

    if decimal_value <= 0:
        raise ValidationError(
            "Purchase amount must be greater than zero."
        )

    return decimal_value


def _normalize_purchase_date(value) -> str:
    if not isinstance(value, date):
        raise ValidationError(
            "Invalid purchase date."
        )

    return value.isoformat()


@transaction.atomic
def submit_currency_purchase_create(
    *,
    maker,
    registration_order: RegistrationOrder,
    amount: Decimal,
    currency: str,
    purchase_date: date,
    reason: str = "",
) -> ApprovalRequest:

    if not maker or not maker.pk:
        raise ValidationError(
            "A valid maker is required."
        )

    if not maker.has_perm(
        "trade_orders.add_currencypurchase"
    ):
        raise ValidationError(
            "You do not have permission to submit "
            "a currency purchase request."
        )

    locked_order = (
        RegistrationOrder.objects
        .select_for_update()
        .get(pk=registration_order.pk)
    )

    currency = currency.strip().upper()

    normalized_amount = _normalize_decimal(
        amount
    )

    validate_purchase_amount(
        registration_order=locked_order,
        purchase_amount=normalized_amount,
        purchase_currency=currency,
    )

    normalized_purchase_date = (
        _normalize_purchase_date(purchase_date)
    )

    return ApprovalRequest.objects.create(
        operation=ApprovalRequest.Operation.CREATE,
        target_type=CURRENCY_PURCHASE_TARGET,
        target_id=None,
        payload={
            "registration_order_id": str(
                locked_order.pk
            ),
            "amount": format(
                normalized_amount,
                "f",
            ),
            "currency": locked_order.currency,
            "purchase_date": normalized_purchase_date,
        },
        reason=reason.strip(),
        maker=maker,
    )