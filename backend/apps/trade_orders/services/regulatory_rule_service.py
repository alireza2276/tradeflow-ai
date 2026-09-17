from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.db import models

from apps.trade_orders.models import PaymentInstrument, RegulatoryRule


def _dimension_query(field_name, value):
    if value:
        return models.Q(**{field_name: value}) | models.Q(**{field_name: ""})
    return models.Q(**{field_name: ""})


def resolve_rule(
    *,
    registration_order,
    event_date: date,
    deadline_kind,
    funding_source_code="",
):
    try:
        instrument = registration_order.payment_instrument
    except PaymentInstrument.DoesNotExist as exc:
        raise ValidationError(
            "A payment instrument is required before a regulatory deadline can be resolved."
        ) from exc

    activity_type = registration_order.activity_type or registration_order.company.company_type
    goods_category_code = (registration_order.goods_category_code or "").strip()
    funding_source_code = (funding_source_code or "").strip()

    rules = (
        RegulatoryRule.objects.filter(
            is_active=True,
            operation_type=instrument.operation_type,
            deadline_kind=deadline_kind,
            effective_from__lte=event_date,
        )
        .filter(models.Q(effective_to__isnull=True) | models.Q(effective_to__gte=event_date))
        .filter(models.Q(activity_type=activity_type) | models.Q(activity_type__isnull=True))
        .filter(_dimension_query("goods_category_code", goods_category_code))
        .filter(_dimension_query("funding_source_code", funding_source_code))
    )

    candidates = list(rules)
    if not candidates:
        return None

    def score(rule):
        specificity = sum(
            (
                bool(rule.activity_type),
                bool(rule.goods_category_code),
                bool(rule.funding_source_code),
            )
        )
        return (rule.priority, -specificity, -rule.effective_from.toordinal(), rule.code)

    candidates.sort(key=score)
    best = candidates[0]
    best_key = score(best)[:3]
    ambiguous = [r for r in candidates[1:] if score(r)[:3] == best_key]
    if ambiguous:
        codes = ", ".join([best.code, *(r.code for r in ambiguous)])
        raise ValidationError(
            f"Regulatory rule configuration is ambiguous for {deadline_kind}: {codes}."
        )
    return best


def get_basis_date(*, rule, purchase_date, remittance_date, instrument):
    if rule.deadline_basis == RegulatoryRule.DeadlineBasis.PURCHASE_DATE:
        return purchase_date
    if rule.deadline_basis == RegulatoryRule.DeadlineBasis.REMITTANCE_DATE:
        if not remittance_date:
            raise ValidationError(
                f"Remittance date is required by regulatory rule {rule.code}."
            )
        return remittance_date
    if rule.deadline_basis == RegulatoryRule.DeadlineBasis.INSTRUMENT_DATE:
        if not instrument.issue_date:
            raise ValidationError(
                f"Payment-instrument date is required by regulatory rule {rule.code}."
            )
        return instrument.issue_date
    raise ValidationError("Unsupported regulatory deadline basis.")


def calculate_rule_deadline(*, rule, basis_date):
    if rule.deadline_months is not None:
        return basis_date + relativedelta(months=rule.deadline_months)
    if rule.deadline_days is not None:
        return basis_date + timedelta(days=rule.deadline_days)
    raise ValidationError(f"Regulatory rule {rule.code} has no valid duration.")


def resolve_purchase_deadlines(
    *,
    registration_order,
    purchase_date,
    remittance_date=None,
    funding_source_code="",
):
    instrument = registration_order.payment_instrument
    resolved = []

    for deadline_kind, _label in RegulatoryRule.DeadlineKind.choices:
        rule = resolve_rule(
            registration_order=registration_order,
            event_date=purchase_date,
            deadline_kind=deadline_kind,
            funding_source_code=funding_source_code,
        )
        if rule is None:
            continue
        basis_date = get_basis_date(
            rule=rule,
            purchase_date=purchase_date,
            remittance_date=remittance_date,
            instrument=instrument,
        )
        resolved.append(
            {
                "deadline_kind": deadline_kind,
                "rule": rule,
                "basis_date": basis_date,
                "deadline": calculate_rule_deadline(rule=rule, basis_date=basis_date),
            }
        )

    if not any(item["deadline_kind"] == RegulatoryRule.DeadlineKind.IMPORT_CLEARANCE for item in resolved):
        raise ValidationError(
            "No active IMPORT_CLEARANCE regulatory rule matches this purchase. "
            "Configure a verified rule before creating the currency purchase."
        )

    return resolved
