from datetime import date
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.trade_orders.services.validation import (
    get_total_shipment_amount,
    validate_purchase_amount,
)
from apps.workflows.models import ApprovalRequest

SHIPMENT_PART_TARGET = "shipment_part"

from apps.trade_orders.models import (
    CurrencyPurchase,
    RegistrationOrder,
    ShipmentPart,
)

from apps.trade_orders.services.validation import (
    validate_purchase_amount,
    validate_shipment_part_amount,
)

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


def _validate_maker(
    *,
    maker,
    permission: str,
) -> None:
    if not maker or not maker.pk:
        raise ValidationError(
            "A valid maker is required."
        )

    if not maker.has_perm(permission):
        raise ValidationError(
            "You do not have permission to submit "
            "this approval request."
        )


@transaction.atomic
def submit_currency_purchase_create(
    *,
    maker,
    registration_order: RegistrationOrder,
    amount: Decimal,
    currency: str,
    purchase_date: date,
    remittance_date: date | None = None,
    reason: str = "",
) -> ApprovalRequest:

    _validate_maker(
        maker=maker,
        permission="trade_orders.add_currencypurchase",
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

    normalized_purchase_date = _normalize_purchase_date(purchase_date)
    normalized_remittance_date = _normalize_purchase_date(
        remittance_date or purchase_date
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
            "remittance_date": normalized_remittance_date,
        },
        reason=reason.strip(),
        maker=maker,
    )


@transaction.atomic
def submit_currency_purchase_correction(
    *,
    maker,
    purchase: CurrencyPurchase,
    amount: Decimal,
    purchase_date: date,
    remittance_date: date | None = None,
    reason: str,
) -> ApprovalRequest:

    _validate_maker(
        maker=maker,
        permission="trade_orders.change_currencypurchase",
    )

    reason = reason.strip()

    if not reason:
        raise ValidationError(
            "A correction reason is required."
        )

    purchase_reference = (
        CurrencyPurchase.objects
        .only("registration_order_id")
        .get(pk=purchase.pk)
    )

    locked_order = (
        RegistrationOrder.objects
        .select_for_update()
        .get(
            pk=purchase_reference.registration_order_id
        )
    )

    locked_purchase = (
        CurrencyPurchase.objects
        .select_for_update()
        .get(pk=purchase.pk)
    )

    if (
        locked_purchase.registration_order_id
        != locked_order.pk
    ):
        raise ValidationError(
            "Currency purchase registration order changed "
            "during the correction operation."
        )

    normalized_amount = _normalize_decimal(
        amount
    )

    total_shipped = get_total_shipment_amount(
        locked_purchase
    )

    if normalized_amount < total_shipped:
        raise ValidationError(
            "Currency purchase amount cannot be lower "
            "than the total shipment amount."
        )

    validate_purchase_amount(
        registration_order=locked_order,
        purchase_amount=normalized_amount,
        purchase_currency=locked_order.currency,
        current_purchase=locked_purchase,
    )

    normalized_purchase_date = _normalize_purchase_date(purchase_date)
    effective_remittance_date = (
        remittance_date
        or locked_purchase.remittance_date
        or purchase_date
    )
    normalized_remittance_date = _normalize_purchase_date(
        effective_remittance_date
    )

    if (
        normalized_amount == locked_purchase.amount
        and purchase_date == locked_purchase.purchase_date
        and effective_remittance_date == (
            locked_purchase.remittance_date or locked_purchase.purchase_date
        )
    ):
        raise ValidationError(
            "The correction does not contain any changes."
        )

    return ApprovalRequest.objects.create(
        operation=ApprovalRequest.Operation.CORRECT,
        target_type=CURRENCY_PURCHASE_TARGET,
        target_id=locked_purchase.pk,
        payload={
            "version": locked_purchase.updated_at.isoformat(),
            "before": {
                "amount": format(
                    locked_purchase.amount,
                    "f",
                ),
                "currency": locked_purchase.currency,
                "purchase_date": locked_purchase.purchase_date.isoformat(),
                "remittance_date": (
                    locked_purchase.remittance_date
                    or locked_purchase.purchase_date
                ).isoformat(),
            },
            "proposed": {
                "amount": format(
                    normalized_amount,
                    "f",
                ),
                "currency": locked_purchase.currency,
                "purchase_date": normalized_purchase_date,
                "remittance_date": normalized_remittance_date,
            },
        },
        reason=reason,
        maker=maker,
    )

@transaction.atomic
def submit_currency_purchase_void(
    *,
    maker,
    purchase: CurrencyPurchase,
    reason: str,
) -> ApprovalRequest:

    _validate_maker(
        maker=maker,
        permission="trade_orders.void_currencypurchase",
    )

    reason = reason.strip()

    if not reason:
        raise ValidationError(
            "A void reason is required."
        )

    purchase_reference = (
        CurrencyPurchase.objects
        .only("registration_order_id")
        .get(pk=purchase.pk)
    )

    locked_order = (
        RegistrationOrder.objects
        .select_for_update()
        .get(
            pk=purchase_reference.registration_order_id
        )
    )

    locked_purchase = (
        CurrencyPurchase.objects
        .select_for_update()
        .get(pk=purchase.pk)
    )

    if (
        locked_purchase.registration_order_id
        != locked_order.pk
    ):
        raise ValidationError(
            "Currency purchase registration order changed "
            "during the void operation."
        )

    if locked_purchase.is_void:
        raise ValidationError(
            "Currency purchase is already void."
        )

    if locked_purchase.shipment_parts.filter(
            is_void=False
    ).exists():
        raise ValidationError(
            "Currency purchase with active shipment parts "
            "cannot be voided."
        )

    return ApprovalRequest.objects.create(
        operation=ApprovalRequest.Operation.VOID,
        target_type=CURRENCY_PURCHASE_TARGET,
        target_id=locked_purchase.pk,
        payload={
            "version": locked_purchase.updated_at.isoformat(),
            "before": {
                "amount": format(
                    locked_purchase.amount,
                    "f",
                ),
                "currency": locked_purchase.currency,
                "purchase_date": (
                    locked_purchase.purchase_date.isoformat()
                ),
                "registration_order_id": str(
                    locked_purchase.registration_order_id
                ),
            },
        },
        reason=reason,
        maker=maker,
    )

def _shipment_snapshot(
    shipment: ShipmentPart,
) -> dict:
    return {
        "currency_purchase_id": str(
            shipment.currency_purchase_id
        ),
        "amount": format(
            shipment.amount,
            "f",
        ),
        "shipment_date": (
            shipment.shipment_date.isoformat()
            if shipment.shipment_date
            else None
        ),
        "received_date": (
            shipment.received_date.isoformat()
            if shipment.received_date
            else None
        ),
        "reference_number":
            shipment.reference_number,
        "notes":
            shipment.notes,
    }

@transaction.atomic
def submit_shipment_part_create(
    *,
    maker,
    currency_purchase: CurrencyPurchase,
    amount: Decimal,
    shipment_date=None,
    received_date=None,
    reference_number="",
    notes="",
    reason: str = "",
) -> ApprovalRequest:
    if not maker or not maker.pk:
        raise ValidationError(
            "A valid maker is required."
        )

    if not maker.has_perm(
        "trade_orders.add_shipmentpart"
    ):
        raise ValidationError(
            "You do not have permission to submit "
            "a shipment part request."
        )

    locked_purchase = (
        CurrencyPurchase.objects
        .select_for_update()
        .get(pk=currency_purchase.pk)
    )

    if locked_purchase.is_void:
        raise ValidationError(
            "Shipment cannot be registered for a voided "
            "currency purchase."
        )

    validate_shipment_part_amount(
        currency_purchase=locked_purchase,
        shipment_amount=amount,
    )

    return ApprovalRequest.objects.create(
        operation=ApprovalRequest.Operation.CREATE,
        target_type=SHIPMENT_PART_TARGET,
        target_id=None,
        payload={
            "currency_purchase_id": str(
                locked_purchase.pk
            ),
            "amount": format(amount, "f"),
            "shipment_date": (
                shipment_date.isoformat()
                if shipment_date
                else None
            ),
            "received_date": (
                received_date.isoformat()
                if received_date
                else None
            ),
            "reference_number":
                reference_number.strip(),
            "notes": notes,
        },
        reason=reason.strip(),
        maker=maker,
    )

@transaction.atomic
def submit_shipment_part_correction(
    *,
    maker,
    shipment: ShipmentPart,
    amount: Decimal,
    shipment_date=None,
    received_date=None,
    reference_number="",
    notes="",
    reason: str,
) -> ApprovalRequest:
    if not maker or not maker.pk:
        raise ValidationError(
            "A valid maker is required."
        )

    if not maker.has_perm(
        "trade_orders.change_shipmentpart"
    ):
        raise ValidationError(
            "You do not have permission to submit "
            "a shipment correction request."
        )

    reason = reason.strip()

    if not reason:
        raise ValidationError(
            "A correction reason is required."
        )

    locked_shipment = (
        ShipmentPart.objects
        .select_for_update()
        .select_related("currency_purchase")
        .get(pk=shipment.pk)
    )

    if locked_shipment.is_void:
        raise ValidationError(
            "Voided shipment part cannot be corrected."
        )

    if locked_shipment.currency_purchase.is_void:
        raise ValidationError(
            "Shipment cannot be corrected for a voided "
            "currency purchase."
        )

    validate_shipment_part_amount(
        currency_purchase=locked_shipment.currency_purchase,
        shipment_amount=amount,
        current_shipment=locked_shipment,
    )

    if (
        hasattr(locked_shipment, "invoice")
        and amount != locked_shipment.amount
    ):
        raise ValidationError(
            "Shipment part amount cannot be changed "
            "after an invoice has been issued."
        )

    return ApprovalRequest.objects.create(
        operation=ApprovalRequest.Operation.CORRECT,
        target_type=SHIPMENT_PART_TARGET,
        target_id=locked_shipment.pk,
        payload={
            "version":
                locked_shipment.updated_at.isoformat(),
            "before":
                _shipment_snapshot(locked_shipment),
            "proposed": {
                "currency_purchase_id": str(
                    locked_shipment.currency_purchase_id
                ),
                "amount": format(amount, "f"),
                "shipment_date": (
                    shipment_date.isoformat()
                    if shipment_date
                    else None
                ),
                "received_date": (
                    received_date.isoformat()
                    if received_date
                    else None
                ),
                "reference_number":
                    reference_number.strip(),
                "notes": notes,
            },
        },
        reason=reason,
        maker=maker,
    )

@transaction.atomic
def submit_shipment_part_void(
    *,
    maker,
    shipment: ShipmentPart,
    reason: str,
) -> ApprovalRequest:
    if not maker or not maker.pk:
        raise ValidationError(
            "A valid maker is required."
        )

    if not maker.has_perm(
        "trade_orders.void_shipmentpart"
    ):
        raise ValidationError(
            "You do not have permission to submit "
            "a shipment void request."
        )

    reason = reason.strip()

    if not reason:
        raise ValidationError(
            "A void reason is required."
        )

    locked_shipment = (
        ShipmentPart.objects
        .select_for_update()
        .select_related("currency_purchase")
        .get(pk=shipment.pk)
    )

    if locked_shipment.is_void:
        raise ValidationError(
            "Shipment part is already void."
        )

    if locked_shipment.currency_purchase.is_void:
        raise ValidationError(
            "Shipment belongs to a voided currency purchase."
        )

    if hasattr(locked_shipment, "invoice"):
        raise ValidationError(
            "Shipment part with an invoice cannot be voided."
        )

    return ApprovalRequest.objects.create(
        operation=ApprovalRequest.Operation.VOID,
        target_type=SHIPMENT_PART_TARGET,
        target_id=locked_shipment.pk,
        payload={
            "version":
                locked_shipment.updated_at.isoformat(),
            "before":
                _shipment_snapshot(locked_shipment),
        },
        reason=reason,
        maker=maker,
    )