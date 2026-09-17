from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.companies.models import Company
from apps.trade_orders.models import (
    CurrencyPurchase, CustomsClearance, PaymentInstrument, RegistrationOrder,
    RegulatoryDeadline, RegulatoryRule,
)
from apps.trade_orders.services.compliance_service import derive_obligation_status, extend_deadline
from apps.trade_orders.services.purchase_service import create_currency_purchase
from apps.trade_orders.services.regulatory_rule_service import resolve_purchase_deadlines


class RegulatoryComplianceTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Rule Test Co", national_id="12345678901", company_type="COMMERCIAL")
        self.order = RegistrationOrder.objects.create(
            company=self.company, order_number="R-1", registered_amount=Decimal("100000"),
            currency="EUR", activity_type="COMMERCIAL", goods_category_code="TEST_GOODS",
        )
        self.instrument = PaymentInstrument.objects.create(
            registration_order=self.order, instrument_number="PI-R-1",
            operation_type="REMITTANCE", issue_date=date(2026, 9, 1),
        )
        self.import_rule = RegulatoryRule.objects.create(
            code="TEST-IMPORT-180D", operation_type="REMITTANCE", activity_type="COMMERCIAL",
            goods_category_code="TEST_GOODS", funding_source_code="TEST_SOURCE",
            deadline_kind="IMPORT_CLEARANCE", deadline_basis="PURCHASE_DATE",
            deadline_days=180, effective_from=date(2026, 1, 1),
        )
        self.shipping_rule = RegulatoryRule.objects.create(
            code="TEST-SHIPPING-30D", operation_type="REMITTANCE", activity_type="COMMERCIAL",
            goods_category_code="TEST_GOODS", funding_source_code="TEST_SOURCE",
            deadline_kind="SHIPPING_DOCUMENTS", deadline_basis="REMITTANCE_DATE",
            deadline_days=30, effective_from=date(2026, 1, 1),
        )

    def test_purchase_has_independent_regulatory_deadlines(self):
        purchase = create_currency_purchase(
            registration_order=self.order, amount=Decimal("100"), currency="EUR",
            purchase_date=date(2026, 9, 10), remittance_date=date(2026, 9, 15),
            funding_source_code="TEST_SOURCE",
        )
        deadlines = {d.deadline_kind: d for d in purchase.regulatory_deadlines.all()}
        self.assertEqual(deadlines["IMPORT_CLEARANCE"].basis_date, date(2026, 9, 10))
        self.assertEqual(deadlines["IMPORT_CLEARANCE"].original_deadline, date(2027, 3, 9))
        self.assertEqual(deadlines["SHIPPING_DOCUMENTS"].basis_date, date(2026, 9, 15))
        self.assertEqual(deadlines["SHIPPING_DOCUMENTS"].original_deadline, date(2026, 10, 15))

    def test_remittance_date_is_not_silently_replaced_by_purchase_date(self):
        with self.assertRaises(ValidationError):
            resolve_purchase_deadlines(
                registration_order=self.order, purchase_date=date(2026, 9, 10),
                remittance_date=None, funding_source_code="TEST_SOURCE",
            )

    def test_rule_engine_fails_closed_without_import_rule(self):
        self.import_rule.is_active = False
        self.import_rule.save(update_fields=("is_active",))
        with self.assertRaises(ValidationError):
            resolve_purchase_deadlines(
                registration_order=self.order, purchase_date=date(2026, 9, 10),
                remittance_date=date(2026, 9, 15), funding_source_code="TEST_SOURCE",
            )

    def test_extension_changes_only_selected_deadline(self):
        user = get_user_model().objects.create_user(username="checker", password="x")
        purchase = create_currency_purchase(
            registration_order=self.order, amount=Decimal("100"), currency="EUR",
            purchase_date=date(2026, 9, 10), remittance_date=date(2026, 9, 15),
            funding_source_code="TEST_SOURCE",
        )
        shipping_before = purchase.regulatory_deadlines.get(deadline_kind="SHIPPING_DOCUMENTS").effective_deadline
        event = extend_deadline(
            purchase=purchase, new_deadline=date(2027, 4, 8), reason="Approved extension",
            approved_by=user, reference="REF-1", deadline_kind="IMPORT_CLEARANCE",
        )
        purchase.refresh_from_db()
        shipping_after = purchase.regulatory_deadlines.get(deadline_kind="SHIPPING_DOCUMENTS").effective_deadline
        self.assertEqual(purchase.original_deadline, date(2027, 3, 9))
        self.assertEqual(purchase.deadline, date(2027, 4, 8))
        self.assertEqual(event.regulatory_deadline.deadline_kind, "IMPORT_CLEARANCE")
        self.assertEqual(shipping_before, shipping_after)

    def test_clearance_does_not_automatically_mean_fx_settled(self):
        purchase = create_currency_purchase(
            registration_order=self.order, amount=Decimal("100"), currency="EUR",
            purchase_date=date(2026, 9, 10), remittance_date=date(2026, 9, 15),
            funding_source_code="TEST_SOURCE",
        )
        CustomsClearance.objects.create(
            currency_purchase=purchase, declaration_number="C-1", clearance_date=date(2026, 10, 1),
            amount=Decimal("100"), status="FINAL",
        )
        self.assertEqual(derive_obligation_status(purchase), CurrencyPurchase.ObligationStatus.CLEARED)
        self.assertIsNone(purchase.obligation_settled_at)
