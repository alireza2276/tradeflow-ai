from decimal import Decimal

from django.utils import timezone

from apps.trade_orders.models import (
    CurrencyPurchase,
    RegistrationOrder,
)
from apps.trade_orders.services.balance_service import (
    get_purchase_balance,
)


def get_dashboard_summary():
    today = timezone.localdate()

    active_orders = RegistrationOrder.objects.filter(
        is_active=True,
    )

    active_purchases = (
        CurrencyPurchase.objects
        .filter(
            registration_order__is_active=True,
        )
        .select_related(
            "registration_order",
            "registration_order__company",
        )
        .prefetch_related(
            "shipment_parts",
        )
    )

    overdue_count = 0
    due_soon_count = 0

    currency_totals = {}

    attention_cases = []

    for purchase in active_purchases:
        balance = get_purchase_balance(
            purchase=purchase,
        )

        documented_amount = balance["documented_amount"]
        remaining_amount = balance["remaining_amount"]

        currency = purchase.currency

        if currency not in currency_totals:
            currency_totals[currency] = {
                "purchased_amount": Decimal("0"),
                "documented_amount": Decimal("0"),
                "remaining_amount": Decimal("0"),
            }

        currency_totals[currency]["purchased_amount"] += (
            purchase.amount
        )

        currency_totals[currency]["documented_amount"] += (
            documented_amount
        )

        currency_totals[currency]["remaining_amount"] += (
            remaining_amount
        )

        if remaining_amount <= 0:
            continue

        days_remaining = (
            purchase.deadline - today
        ).days

        if days_remaining <= 30:
            attention_cases.append(
                {
                    "purchase_id": str(purchase.id),
                    "company_name": purchase.registration_order.company.name,
                    "order_number": purchase.registration_order.order_number,
                    "currency": purchase.currency,
                    "remaining_amount": remaining_amount,
                    "deadline": purchase.deadline,
                    "days_remaining": days_remaining,
                    "status": (
                        "OVERDUE"
                        if days_remaining < 0
                        else "DUE_SOON"
                    ),
                }
            )

        if days_remaining < 0:
            overdue_count += 1

        elif days_remaining <= 30:
            due_soon_count += 1

    attention_cases.sort(
        key=lambda case: case["days_remaining"]
    )

    return {
        "active_orders_count": active_orders.count(),
        "active_purchases_count": len(active_purchases),
        "due_soon_count": due_soon_count,
        "overdue_count": overdue_count,
        "currency_totals": currency_totals,
        "attention_cases": attention_cases,
    }