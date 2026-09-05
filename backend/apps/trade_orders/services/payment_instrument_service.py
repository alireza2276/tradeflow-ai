from django.db import IntegrityError, transaction
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

    locked_order = (
        RegistrationOrder.objects
        .select_for_update()
        .get(pk=registration_order.pk)
    )

    if PaymentInstrument.objects.filter(
        registration_order=locked_order
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

    try:
        with transaction.atomic():
            return PaymentInstrument.objects.create(
                registration_order=locked_order,
                instrument_number=instrument_number,
            )

    except IntegrityError:
        if PaymentInstrument.objects.filter(
                registration_order=locked_order
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

        raise

@transaction.atomic
def update_payment_instrument(
    *,
    payment_instrument: PaymentInstrument,
    instrument_number: str,
) -> PaymentInstrument:

    instrument_number = instrument_number.strip()

    if not instrument_number:
        raise ValidationError(
            "Payment instrument number cannot be empty."
        )

    locked_order = (
        RegistrationOrder.objects
        .select_for_update()
        .get(
            pk=payment_instrument.registration_order_id
        )
    )

    locked_payment_instrument = (
        PaymentInstrument.objects
        .select_for_update()
        .get(
            pk=payment_instrument.pk
        )
    )

    if PaymentInstrument.objects.filter(
        instrument_number=instrument_number
    ).exclude(
        pk=locked_payment_instrument.pk
    ).exists():
        raise ValidationError(
            "This payment instrument number already exists."
        )

    locked_payment_instrument.registration_order = (
        locked_order
    )

    locked_payment_instrument.instrument_number = (
        instrument_number
    )

    try:
        with transaction.atomic():
            locked_payment_instrument.save(
                update_fields=(
                    "registration_order",
                    "instrument_number",
                    "updated_at",
                )
            )

    except IntegrityError:
        if PaymentInstrument.objects.filter(
                instrument_number=instrument_number
        ).exclude(
            pk=locked_payment_instrument.pk
        ).exists():
            raise ValidationError(
                "This payment instrument number already exists."
            )

        raise

    return locked_payment_instrument