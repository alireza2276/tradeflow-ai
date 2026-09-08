from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.trade_orders.models import (
    CurrencyPurchase,
    ShipmentPart,
)


@transaction.atomic
def create_shipment_part(
    *,
    currency_purchase: CurrencyPurchase,
    amount: Decimal,
    shipment_date=None,
    received_date=None,
    reference_number="",
    notes="",
) -> ShipmentPart:
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

    if amount <= Decimal("0"):
        raise ValidationError(
            "Shipment part amount must be greater than zero."
        )

    existing_amount = sum(
        (
            part.amount
            for part in locked_purchase.shipment_parts.all()
        ),
        Decimal("0"),
    )

    remaining_amount = (
        locked_purchase.amount - existing_amount
    )

    if amount > remaining_amount:
        raise ValidationError(
            "Shipment part amount exceeds "
            "the remaining purchase amount."
        )

    return ShipmentPart.objects.create(
        currency_purchase=locked_purchase,
        amount=amount,
        shipment_date=shipment_date,
        received_date=received_date,
        reference_number=reference_number.strip(),
        notes=notes,
    )


@transaction.atomic
def update_shipment_part(
    *,
    shipment: ShipmentPart,
    amount: Decimal,
    shipment_date=None,
    received_date=None,
    reference_number="",
    notes="",
) -> ShipmentPart:
    shipment_reference = (
        ShipmentPart.objects
        .only("currency_purchase_id")
        .get(pk=shipment.pk)
    )

    locked_purchase = (
        CurrencyPurchase.objects
        .select_for_update()
        .get(pk=shipment_reference.currency_purchase_id)
    )

    locked_shipment = (
        ShipmentPart.objects
        .select_for_update()
        .get(pk=shipment.pk)
    )

    if (
        locked_shipment.currency_purchase_id
        != locked_purchase.pk
    ):
        raise ValidationError(
            "Shipment currency purchase changed "
            "during the update operation."
        )

    if locked_purchase.is_void:
        raise ValidationError(
            "Shipment cannot be updated for a voided "
            "currency purchase."
        )

    if (
        hasattr(locked_shipment, "invoice")
        and amount != locked_shipment.amount
    ):
        raise ValidationError(
            "Shipment part amount cannot be changed "
            "after an invoice has been issued."
        )

    if amount <= Decimal("0"):
        raise ValidationError(
            "Shipment part amount must be greater than zero."
        )

    other_shipments_amount = sum(
        (
            part.amount
            for part in locked_purchase.shipment_parts.exclude(
                pk=locked_shipment.pk
            )
        ),
        Decimal("0"),
    )

    remaining_amount = (
        locked_purchase.amount - other_shipments_amount
    )

    if amount > remaining_amount:
        raise ValidationError(
            "Shipment part amount exceeds "
            "the remaining purchase amount."
        )

    locked_shipment.amount = amount
    locked_shipment.shipment_date = shipment_date
    locked_shipment.received_date = received_date
    locked_shipment.reference_number = (
        reference_number.strip()
    )
    locked_shipment.notes = notes

    locked_shipment.save(
        update_fields=(
            "amount",
            "shipment_date",
            "received_date",
            "reference_number",
            "notes",
            "updated_at",
        )
    )

    return locked_shipment