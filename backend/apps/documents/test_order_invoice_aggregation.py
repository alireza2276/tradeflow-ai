from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.companies.models import Company
from apps.documents.serializers import InvoiceSerializer
from apps.documents.services.invoice_service import create_invoice
from apps.trade_orders.models import RegistrationOrder
from apps.trade_orders.services.purchase_service import create_currency_purchase
from apps.trade_orders.services.shipment_service import create_shipment_part


class OrderInvoiceAggregationTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="Invoice Aggregation Company",
            national_id="8877665544",
            company_type="COMMERCIAL",
        )
        self.order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="INV-AGG-001",
            registered_amount=Decimal("150000"),
            currency="EUR",
        )

    def _create_invoice_for_purchase(self, purchase, amount, reference):
        shipment = create_shipment_part(
            currency_purchase=purchase,
            amount=amount,
            shipment_date=date(2026, 9, 1),
            received_date=date(2026, 9, 5),
            reference_number=reference,
        )
        return create_invoice(
            shipment_part=shipment,
            fob_amount=amount,
            freight_amount=Decimal("0"),
            submission_date=date(2026, 9, 10),
        )

    def test_existing_invoice_remaining_stays_with_its_purchase(self):
        first_purchase = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("145000"),
            currency="EUR",
            purchase_date=date(2026, 7, 1),
        )
        first_invoice = self._create_invoice_for_purchase(
            first_purchase,
            Decimal("145000"),
            "INV-AGG-SHIP-1",
        )

        before = InvoiceSerializer(first_invoice).data
        self.assertEqual(before["order_total_purchased"], "145000.0000")
        self.assertEqual(before["remaining_amount"], "0.0000")

        second_purchase = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("5000"),
            currency="EUR",
            purchase_date=date(2026, 8, 1),
        )

        after = InvoiceSerializer(first_invoice).data
        self.assertEqual(after["order_total_purchased"], "150000.0000")
        self.assertEqual(after["remaining_amount"], "0.0000")
        self.assertNotEqual(first_purchase.deadline, second_purchase.deadline)

    def test_document_parts_are_numbered_per_currency_purchase(self):
        first_purchase = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("145000"),
            currency="EUR",
            purchase_date=date(2026, 7, 1),
        )
        second_purchase = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("5000"),
            currency="EUR",
            purchase_date=date(2026, 8, 1),
        )

        first_invoice = self._create_invoice_for_purchase(
            first_purchase,
            Decimal("145000"),
            "INV-AGG-SHIP-1",
        )
        second_invoice = self._create_invoice_for_purchase(
            second_purchase,
            Decimal("5000"),
            "INV-AGG-SHIP-2",
        )

        data = InvoiceSerializer(
            [first_invoice, second_invoice],
            many=True,
        ).data

        self.assertEqual(data[0]["document_part_number"], 1)
        self.assertEqual(data[0]["remaining_amount"], "0.0000")
        self.assertEqual(data[1]["document_part_number"], 1)
        self.assertEqual(data[1]["remaining_amount"], "0.0000")
        self.assertEqual(data[0]["order_total_purchased"], "150000.0000")
        self.assertEqual(data[1]["order_total_purchased"], "150000.0000")
