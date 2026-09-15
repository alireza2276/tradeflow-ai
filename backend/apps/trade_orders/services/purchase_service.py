from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.trade_orders.models import (
    CurrencyPurchase,
    RegistrationOrder,
)
from apps.trade_orders.services.deadline_service import (
    calculate_purchase_deadline,
)
from apps.trade_orders.services.validation import (
    get_total_shipment_amount,
    validate_purchase_amount,
)


@transaction.atomic
def create_currency_purchase(
    *,
    registration_order: RegistrationOrder,
    amount: Decimal,
    currency: str,
    purchase_date: date,
    remittance_date: date | None = None,
) -> CurrencyPurchase:
    locked_order = (
        RegistrationOrder.objects
        .select_for_update()
        .select_related("company")
        .get(pk=registration_order.pk)
    )

    validate_purchase_amount(
        registration_order=locked_order,
        purchase_amount=amount,
        purchase_currency=currency,
    )


    effective_remittance_date = remittance_date or purchase_date
    deadline = calculate_purchase_deadline(
        remittance_date=effective_remittance_date,
        activity_type=(
            locked_order.activity_type
            or locked_order.company.company_type
        ),
        configured_months=locked_order.shipment_deadline_months,
    )

    return CurrencyPurchase.objects.create(
        registration_order=locked_order,
        amount=amount,
        currency=locked_order.currency,
        purchase_date=purchase_date,
        remittance_date=effective_remittance_date,
        original_deadline=deadline,
        deadline=deadline,
    )


@transaction.atomic
def update_currency_purchase(
    *,
    purchase: CurrencyPurchase,
    amount: Decimal,
    purchase_date: date,
    remittance_date: date | None = None,
) -> CurrencyPurchase:
    purchase_reference = (
        CurrencyPurchase.objects
        .only("registration_order_id")
        .get(pk=purchase.pk)
    )

    locked_order = (
        RegistrationOrder.objects
        .select_for_update()
        .select_related("company")
        .get(pk=purchase_reference.registration_order_id)
    )

    locked_purchase = (
        CurrencyPurchase.objects
        .select_for_update()
        .select_related(
            "registration_order",
            "registration_order__company",
        )
        .get(pk=purchase.pk)
    )

    if (
        locked_purchase.registration_order_id
        != locked_order.pk
    ):
        raise ValidationError(
            "Currency purchase registration order changed "
            "during the update operation."
        )

    if locked_purchase.is_void:
        raise ValidationError(
            "Voided currency purchase cannot be corrected."
        )

    total_shipped = get_total_shipment_amount(
        locked_purchase
    )

    if amount < total_shipped:
        raise ValidationError(
            "Currency purchase amount cannot be lower "
            "than the total shipment amount."
        )

    validate_purchase_amount(
        registration_order=locked_order,
        purchase_amount=amount,
        purchase_currency=locked_order.currency,
        current_purchase=locked_purchase,
    )

    effective_remittance_date = (
        remittance_date
        or locked_purchase.remittance_date
        or purchase_date
    )
    deadline = calculate_purchase_deadline(
        remittance_date=effective_remittance_date,
        activity_type=(
            locked_order.activity_type
            or locked_order.company.company_type
        ),
        configured_months=locked_order.shipment_deadline_months,
    )

    locked_purchase.amount = amount
    locked_purchase.currency = locked_order.currency
    locked_purchase.purchase_date = purchase_date
    locked_purchase.remittance_date = effective_remittance_date
    locked_purchase.original_deadline = deadline
    locked_purchase.deadline = deadline
    locked_purchase.deadline_extension_reference = ""
    locked_purchase.deadline_extension_reason = ""

    locked_purchase.save(
        update_fields=(
            "amount",
            "currency",
            "purchase_date",
            "remittance_date",
            "original_deadline",
            "deadline",
            "deadline_extension_reference",
            "deadline_extension_reason",
            "updated_at",
        )
    )

    return locked_purchase
