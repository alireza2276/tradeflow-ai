from decimal import Decimal

from django.core.exceptions import ValidationError

from apps.trade_orders.models import (
    CurrencyPurchase,
    RegistrationOrder,
    ShipmentPart,
)


def get_total_purchased_amount(registration_order):
    return sum(
        (
            purchase.amount
            for purchase
            in registration_order.currency_purchases.filter(
                is_void=False
            )
        ),
        Decimal("0"),
    )


def validate_purchase_amount(
    registration_order: RegistrationOrder,
    purchase_amount: Decimal,
    purchase_currency: str,
    current_purchase: CurrencyPurchase | None = None,
) -> None:
    if not registration_order.is_active:
        raise ValidationError(
            "Cannot create or update a currency purchase "
            "for an inactive registration order."
        )
    if purchase_currency != registration_order.currency:
        raise ValidationError(
            "Purchase currency must match registration order currency."
        )

    if purchase_amount <= 0:
        raise ValidationError(
            "Purchase amount must be greater than zero."
        )

    total_purchased = get_total_purchased_amount(
        registration_order
    )

    if (
            current_purchase is not None
            and not current_purchase.is_void
    ):
        total_purchased -= current_purchase.amount

    if total_purchased + purchase_amount > registration_order.registered_amount:
        raise ValidationError(
            "Total currency purchases cannot exceed "
            "the registration order amount."
        )


def get_total_shipment_amount(
    currency_purchase: CurrencyPurchase,
) -> Decimal:
    return sum(
        (
            shipment.amount
            for shipment in currency_purchase.shipment_parts.all()
        ),
        Decimal("0"),
    )


def validate_shipment_part_amount(
    currency_purchase: CurrencyPurchase,
    shipment_amount: Decimal,
    current_shipment: ShipmentPart | None = None,
) -> None:
    if currency_purchase.is_void:
        raise ValidationError(
            "Shipment cannot be registered for a voided "
            "currency purchase."
        )

    if shipment_amount <= 0:
        raise ValidationError(
            "Shipment part amount must be greater than zero."
        )

    total_shipment = get_total_shipment_amount(
        currency_purchase
    )

    if current_shipment is not None:
        total_shipment -= current_shipment.amount

    if total_shipment + shipment_amount > currency_purchase.amount:
        raise ValidationError(
            "Total shipment amounts cannot exceed "
            "the currency purchase amount."
        )


def validate_invoice_amount(
    shipment_part: ShipmentPart,
    fob_amount: Decimal,
    freight_amount: Decimal,
) -> Decimal:
    if fob_amount < 0:
        raise ValidationError(
            "FOB amount cannot be negative."
        )

    if freight_amount < 0:
        raise ValidationError(
            "Freight amount cannot be negative."
        )

    total_amount = fob_amount + freight_amount

    if total_amount != shipment_part.amount:
        raise ValidationError(
            "Invoice total must equal the shipment part amount."
        )

    return total_amount