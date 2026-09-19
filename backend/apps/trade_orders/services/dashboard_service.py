from decimal import Decimal

from django.db.models import (
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
    Q,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.common.services.date_service import format_dual_date
from apps.trade_orders.models import CurrencyPurchase, RegistrationOrder, ShipmentPart


MONEY_FIELD = DecimalField(max_digits=20, decimal_places=4)
ZERO_MONEY = Value(Decimal("0"), output_field=MONEY_FIELD)


def _active_purchase_queryset():
    """Return active purchases with their non-void shipment balance in SQL.

    Keeping the aggregation in PostgreSQL avoids loading every shipment row
    into Python on each dashboard request.
    """
    return (
        CurrencyPurchase.objects
        .filter(
            registration_order__is_active=True,
            is_void=False,
        )
        .annotate(
            documented_amount_db=Coalesce(
                Sum(
                    "shipment_parts__amount",
                    filter=Q(shipment_parts__is_void=False),
                ),
                ZERO_MONEY,
                output_field=MONEY_FIELD,
            )
        )
        .annotate(
            remaining_amount_db=ExpressionWrapper(
                F("amount") - F("documented_amount_db"),
                output_field=MONEY_FIELD,
            )
        )
    )


def get_dashboard_summary():
    today = timezone.localdate()
    due_soon_end = today + timezone.timedelta(days=30)

    active_purchases = _active_purchase_queryset()

    counts = active_purchases.aggregate(
        active_purchases_count=Count("id"),
        overdue_count=Count(
            "id",
            filter=Q(
                remaining_amount_db__gt=0,
                deadline__lt=today,
            ),
        ),
        due_soon_count=Count(
            "id",
            filter=Q(
                remaining_amount_db__gt=0,
                deadline__gte=today,
                deadline__lte=due_soon_end,
            ),
        ),
    )

    currency_totals = {}

    purchase_currency_rows = (
        CurrencyPurchase.objects
        .filter(
            registration_order__is_active=True,
            is_void=False,
        )
        .values("currency")
        .annotate(purchased_amount=Sum("amount"))
        .order_by("currency")
    )

    shipment_currency_rows = (
        ShipmentPart.objects
        .filter(
            is_void=False,
            currency_purchase__is_void=False,
            currency_purchase__registration_order__is_active=True,
        )
        .values(currency=F("currency_purchase__currency"))
        .annotate(documented_amount=Sum("amount"))
        .order_by("currency")
    )

    documented_by_currency = {
        row["currency"]: row["documented_amount"]
        for row in shipment_currency_rows
    }

    for row in purchase_currency_rows:
        currency = row["currency"]
        purchased_amount = row["purchased_amount"] or Decimal("0")
        documented_amount = documented_by_currency.get(currency, Decimal("0"))
        currency_totals[currency] = {
            "purchased_amount": purchased_amount,
            "documented_amount": documented_amount,
            "remaining_amount": purchased_amount - documented_amount,
        }

    attention_rows = (
        active_purchases
        .filter(
            remaining_amount_db__gt=0,
            deadline__lte=due_soon_end,
        )
        .select_related(
            "registration_order",
            "registration_order__company",
        )
        .order_by("deadline", "id")
        .values(
            "id",
            "registration_order__company__name",
            "registration_order__order_number",
            "currency",
            "remaining_amount_db",
            "deadline",
        )
    )

    attention_cases = []
    for row in attention_rows:
        deadline = row["deadline"]
        days_remaining = (deadline - today).days
        attention_cases.append(
            {
                "purchase_id": str(row["id"]),
                "company_name": row["registration_order__company__name"],
                "order_number": row["registration_order__order_number"],
                "currency": row["currency"],
                "remaining_amount": row["remaining_amount_db"],
                "deadline": deadline,
                "deadline_dual": format_dual_date(deadline),
                "days_remaining": days_remaining,
                "status": "OVERDUE" if days_remaining < 0 else "DUE_SOON",
            }
        )

    return {
        "active_orders_count": RegistrationOrder.objects.filter(
            is_active=True,
        ).count(),
        "active_purchases_count": counts["active_purchases_count"],
        "due_soon_count": counts["due_soon_count"],
        "overdue_count": counts["overdue_count"],
        "currency_totals": currency_totals,
        "attention_cases": attention_cases,
    }
