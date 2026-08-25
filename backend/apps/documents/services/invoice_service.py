from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.documents.models import Invoice
from apps.trade_orders.models import ShipmentPart


@transaction.atomic
def create_invoice(
    *,
    shipment_part: ShipmentPart,
    fob_amount: Decimal,
    freight_amount: Decimal = Decimal("0"),
    submission_date=None,
) -> Invoice:

    if fob_amount < Decimal("0"):
        raise ValidationError(
            "FOB amount cannot be negative."
        )

    if freight_amount < Decimal("0"):
        raise ValidationError(
            "Freight amount cannot be negative."
        )

    if Invoice.objects.filter(
        shipment_part=shipment_part
    ).exists():
        raise ValidationError(
            "This shipment part already has an invoice."
        )

    total_amount = fob_amount + freight_amount

    if total_amount != shipment_part.amount:
        raise ValidationError(
            "Invoice total must equal shipment part amount."
        )

    return Invoice.objects.create(
        shipment_part=shipment_part,
        fob_amount=fob_amount,
        freight_amount=freight_amount,
        submission_date=submission_date,
    )