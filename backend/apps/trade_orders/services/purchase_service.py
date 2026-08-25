from decimal import Decimal
from datetime import date

from django.db import transaction

from apps.trade_orders.models import CurrencyPurchase, RegistrationOrder
from apps.trade_orders.services.deadline_service import (
    calculate_purchase_deadline,
)
from apps.trade_orders.services.validation import validate_purchase_amount


@transaction.atomic
def create_currency_purchase(
    *,
    registration_order: RegistrationOrder,
    amount: Decimal,
    currency: str,
    purchase_date: date,
) -> CurrencyPurchase:

    validate_purchase_amount(
        registration_order=registration_order,
        purchase_amount=amount,
    )

    company_type = registration_order.company.company_type

    deadline = calculate_purchase_deadline(
        purchase_date=purchase_date,
        company_type=company_type,
    )

    return CurrencyPurchase.objects.create(
        registration_order=registration_order,
        amount=amount,
        currency=currency,
        purchase_date=purchase_date,
        deadline=deadline,
    )