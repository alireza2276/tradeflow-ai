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

    if amount <= Decimal("0"):
        raise ValidationError(
            "Shipment part amount must be greater than zero."
        )

    existing_amount = sum(
        (
            part.amount
            for part in currency_purchase.shipment_parts.all()
        ),
        Decimal("0"),
    )

    remaining_amount = (
        currency_purchase.amount - existing_amount
    )

    if amount > remaining_amount:
        raise ValidationError(
            "Shipment part amount exceeds "
            "the remaining purchase amount."
        )

    return ShipmentPart.objects.create(
        currency_purchase=currency_purchase,
        amount=amount,
        shipment_date=shipment_date,
        received_date=received_date,
        reference_number=reference_number.strip(),
        notes=notes,
    )