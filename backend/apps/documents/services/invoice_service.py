from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

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

    locked_shipment_part = (
        ShipmentPart.objects
        .select_for_update()
        .get(pk=shipment_part.pk)
    )

    if fob_amount < Decimal("0"):
        raise ValidationError(
            "FOB amount cannot be negative."
        )

    if freight_amount < Decimal("0"):
        raise ValidationError(
            "Freight amount cannot be negative."
        )

    total_amount = (
        fob_amount + freight_amount
    )

    if total_amount != locked_shipment_part.amount:
        raise ValidationError(
            "Invoice total must equal shipment part amount."
        )

    try:
        return Invoice.objects.create(
            shipment_part=locked_shipment_part,
            fob_amount=fob_amount,
            freight_amount=freight_amount,
            submission_date=submission_date,
        )
    except IntegrityError:
        raise ValidationError(
            "This shipment part already has an invoice."
        )


@transaction.atomic
def update_invoice(
    *,
    invoice: Invoice,
    fob_amount=None,
    freight_amount=None,
    submission_date=None,
) -> Invoice:

    locked_shipment_part = (
        ShipmentPart.objects
        .select_for_update()
        .get(
            pk=invoice.shipment_part_id
        )
    )

    locked_invoice = (
        Invoice.objects
        .select_for_update()
        .get(
            pk=invoice.pk
        )
    )

    if fob_amount is None:
        fob_amount = locked_invoice.fob_amount

    if freight_amount is None:
        freight_amount = locked_invoice.freight_amount

    if submission_date is None:
        submission_date = locked_invoice.submission_date

    if fob_amount < Decimal("0"):
        raise ValidationError(
            "FOB amount cannot be negative."
        )

    if freight_amount < Decimal("0"):
        raise ValidationError(
            "Freight amount cannot be negative."
        )

    total_amount = (
        fob_amount + freight_amount
    )

    if total_amount != locked_shipment_part.amount:
        raise ValidationError(
            "Invoice total must equal shipment part amount."
        )

    locked_invoice.fob_amount = fob_amount
    locked_invoice.freight_amount = freight_amount
    locked_invoice.submission_date = submission_date

    locked_invoice.save(
        update_fields=(
            "fob_amount",
            "freight_amount",
            "total_amount",
            "submission_date",
            "updated_at",
        )
    )

    return locked_invoice