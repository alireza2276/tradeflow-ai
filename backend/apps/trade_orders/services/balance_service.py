from decimal import Decimal

from apps.trade_orders.models import CurrencyPurchase


def get_purchase_balance(
    *,
    purchase: CurrencyPurchase,
) -> dict:
    total_purchase_amount = purchase.amount

    documented_amount = sum(
        (
            part.amount
            for part in purchase.shipment_parts.all()
        ),
        Decimal("0"),
    )

    remaining_amount = (
        total_purchase_amount - documented_amount
    )

    return {
        "purchase_amount": total_purchase_amount,
        "documented_amount": documented_amount,
        "remaining_amount": remaining_amount,
    }