from django.db import transaction
from django.core.exceptions import ValidationError

from apps.trade_orders.models import (
    PaymentInstrument,
    RegistrationOrder,
)


@transaction.atomic
def create_payment_instrument(
    *,
    registration_order: RegistrationOrder,
    instrument_number: str,
) -> PaymentInstrument:

    instrument_number = instrument_number.strip()

    if not instrument_number:
        raise ValidationError(
            "Payment instrument number cannot be empty."
        )

    if PaymentInstrument.objects.filter(
        registration_order=registration_order
    ).exists():
        raise ValidationError(
            "This registration order already has "
            "a payment instrument."
        )

    if PaymentInstrument.objects.filter(
        instrument_number=instrument_number
    ).exists():
        raise ValidationError(
            "This payment instrument number already exists."
        )

    return PaymentInstrument.objects.create(
        registration_order=registration_order,
        instrument_number=instrument_number,
    )