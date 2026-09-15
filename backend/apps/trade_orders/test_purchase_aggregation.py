from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.companies.models import Company
from apps.trade_orders.models import RegistrationOrder
from apps.trade_orders.serializers import CurrencyPurchaseSerializer
from apps.trade_orders.services.purchase_service import create_currency_purchase


class CurrencyPurchaseAggregationTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="Aggregation Company",
            national_id="9988776655",
            company_type="COMMERCIAL",
        )
        self.order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="AGG-ORDER-001",
            registered_amount=Decimal("150000"),
            currency="EUR",
        )

    def test_multiple_purchases_are_aggregated_but_keep_own_deadlines(self):
        first = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("145000"),
            currency="EUR",
            purchase_date=date(2026, 7, 1),
        )
        second = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("5000"),
            currency="EUR",
            purchase_date=date(2026, 8, 1),
        )

        data = CurrencyPurchaseSerializer(
            [first, second],
            many=True,
        ).data

        self.assertEqual(data[0]["purchase_sequence"], 1)
        self.assertEqual(data[1]["purchase_sequence"], 2)
        self.assertEqual(data[0]["registration_order_amount"], "150000.0000")
        self.assertEqual(data[0]["order_total_purchased"], "145000.0000")
        self.assertEqual(data[1]["order_total_purchased"], "150000.0000")
        self.assertEqual(data[0]["order_remaining_to_purchase"], "5000.0000")
        self.assertEqual(data[1]["order_remaining_to_purchase"], "0.0000")

        self.assertEqual(first.deadline, date(2027, 1, 1))
        self.assertEqual(second.deadline, date(2027, 2, 1))
        self.assertNotEqual(first.deadline, second.deadline)

    def test_partial_purchase_shows_remaining_to_purchase(self):
        purchase = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("145000"),
            currency="EUR",
            purchase_date=date(2026, 7, 1),
        )

        data = CurrencyPurchaseSerializer(purchase).data

        self.assertEqual(data["order_total_purchased"], "145000.0000")
        self.assertEqual(data["order_remaining_to_purchase"], "5000.0000")
