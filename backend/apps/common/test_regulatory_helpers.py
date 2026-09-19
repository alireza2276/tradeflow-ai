"""Test-only helpers for Rule Engine V2 fixtures.

These helpers deliberately create synthetic regulatory data only inside Django's
isolated test database. The durations below preserve historical test behaviour
and MUST NOT be treated as current regulatory guidance or production seed data.
"""
from datetime import date

from apps.trade_orders.models import PaymentInstrument, RegulatoryRule
from apps.trade_orders.services.purchase_service import create_currency_purchase as _create_currency_purchase


def ensure_test_regulatory_context(*, registration_order, issue_date=None):
    activity_type = registration_order.activity_type or registration_order.company.company_type
    issue_date = issue_date or date(2000, 1, 1)

    PaymentInstrument.objects.get_or_create(
        registration_order=registration_order,
        defaults={
            "instrument_number": f"TEST-PI-{registration_order.pk}",
            "operation_type": PaymentInstrument.OperationType.REMITTANCE,
            "issue_date": issue_date,
        },
    )

    RegulatoryRule.objects.get_or_create(
        code=f"TEST-{activity_type}-IMPORT-CLEARANCE",
        defaults={
            "operation_type": PaymentInstrument.OperationType.REMITTANCE,
            "activity_type": activity_type,
            "goods_category_code": "",
            "funding_source_code": "",
            "deadline_kind": RegulatoryRule.DeadlineKind.IMPORT_CLEARANCE,
            "deadline_basis": RegulatoryRule.DeadlineBasis.PURCHASE_DATE,
            "deadline_months": 6,
            "deadline_days": None,
            "effective_from": date(2000, 1, 1),
            "effective_to": None,
            "priority": 999,
            "is_active": True,
            "internal_reference": "TEST-ONLY-NOT-A-REGULATORY-SOURCE",
            "notes": "Synthetic test fixture only; not production regulatory data.",
        },
    )


def create_test_currency_purchase(*, registration_order, amount, currency, purchase_date, remittance_date=None, funding_source_code=""):
    ensure_test_regulatory_context(
        registration_order=registration_order,
        issue_date=purchase_date,
    )
    return _create_currency_purchase(
        registration_order=registration_order,
        amount=amount,
        currency=currency,
        purchase_date=purchase_date,
        remittance_date=remittance_date,
        funding_source_code=funding_source_code,
    )
