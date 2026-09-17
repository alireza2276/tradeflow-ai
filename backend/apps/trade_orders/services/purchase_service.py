from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.trade_orders.models import CurrencyPurchase, RegistrationOrder, RegulatoryDeadline, RegulatoryRule
from apps.trade_orders.services.regulatory_rule_service import resolve_purchase_deadlines
from apps.trade_orders.services.validation import get_total_shipment_amount, validate_purchase_amount


def _primary_deadline(resolved):
    return next(item for item in resolved if item["deadline_kind"] == RegulatoryRule.DeadlineKind.IMPORT_CLEARANCE)


def _create_deadline_rows(*, purchase, resolved):
    for item in resolved:
        RegulatoryDeadline.objects.create(
            currency_purchase=purchase,
            deadline_kind=item["deadline_kind"],
            applied_rule=item["rule"],
            basis_date=item["basis_date"],
            original_deadline=item["deadline"],
            effective_deadline=item["deadline"],
        )


@transaction.atomic
def create_currency_purchase(
    *, registration_order: RegistrationOrder, amount: Decimal, currency: str,
    purchase_date: date, remittance_date: date | None = None,
    funding_source_code: str = "",
) -> CurrencyPurchase:
    locked_order = RegistrationOrder.objects.select_for_update().select_related("company").get(pk=registration_order.pk)
    validate_purchase_amount(registration_order=locked_order, purchase_amount=amount, purchase_currency=currency)

    resolved = resolve_purchase_deadlines(
        registration_order=locked_order,
        purchase_date=purchase_date,
        remittance_date=remittance_date,
        funding_source_code=funding_source_code,
    )
    primary = _primary_deadline(resolved)

    purchase = CurrencyPurchase.objects.create(
        registration_order=locked_order,
        amount=amount,
        currency=locked_order.currency,
        purchase_date=purchase_date,
        remittance_date=remittance_date,
        funding_source_code=(funding_source_code or "").strip(),
        original_deadline=primary["deadline"],
        deadline=primary["deadline"],
        applied_rule=primary["rule"],
    )
    _create_deadline_rows(purchase=purchase, resolved=resolved)
    return purchase


@transaction.atomic
def update_currency_purchase(
    *, purchase: CurrencyPurchase, amount: Decimal, purchase_date: date,
    remittance_date: date | None = None, funding_source_code: str | None = None,
) -> CurrencyPurchase:
    purchase_reference = CurrencyPurchase.objects.only("registration_order_id").get(pk=purchase.pk)
    locked_order = RegistrationOrder.objects.select_for_update().select_related("company").get(pk=purchase_reference.registration_order_id)
    locked_purchase = CurrencyPurchase.objects.select_for_update().select_related("registration_order", "registration_order__company").get(pk=purchase.pk)

    if locked_purchase.registration_order_id != locked_order.pk:
        raise ValidationError("Currency purchase registration order changed during the update operation.")
    if locked_purchase.is_void:
        raise ValidationError("Voided currency purchase cannot be corrected.")

    total_shipped = get_total_shipment_amount(locked_purchase)
    if amount < total_shipped:
        raise ValidationError("Currency purchase amount cannot be lower than the total shipment amount.")

    validate_purchase_amount(
        registration_order=locked_order,
        purchase_amount=amount,
        purchase_currency=locked_order.currency,
        current_purchase=locked_purchase,
    )

    new_funding = locked_purchase.funding_source_code if funding_source_code is None else funding_source_code.strip()
    regulatory_inputs_changed = (
        purchase_date != locked_purchase.purchase_date
        or remittance_date != locked_purchase.remittance_date
        or new_funding != locked_purchase.funding_source_code
    )
    if regulatory_inputs_changed and locked_purchase.deadline_extensions.exists():
        raise ValidationError(
            "Regulatory dates/source cannot be changed after a deadline extension exists. "
            "Void/correct through the controlled workflow instead."
        )

    if regulatory_inputs_changed:
        resolved = resolve_purchase_deadlines(
            registration_order=locked_order,
            purchase_date=purchase_date,
            remittance_date=remittance_date,
            funding_source_code=new_funding,
        )
        primary = _primary_deadline(resolved)
        locked_purchase.regulatory_deadlines.all().delete()
        _create_deadline_rows(purchase=locked_purchase, resolved=resolved)
        locked_purchase.original_deadline = primary["deadline"]
        locked_purchase.deadline = primary["deadline"]
        locked_purchase.applied_rule = primary["rule"]
        locked_purchase.deadline_extension_reference = ""
        locked_purchase.deadline_extension_reason = ""

    locked_purchase.amount = amount
    locked_purchase.currency = locked_order.currency
    locked_purchase.purchase_date = purchase_date
    locked_purchase.remittance_date = remittance_date
    locked_purchase.funding_source_code = new_funding
    locked_purchase.save()
    return locked_purchase
