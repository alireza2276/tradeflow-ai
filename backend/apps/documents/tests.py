from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from datetime import date
from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase

from apps.companies.models import Company
from apps.trade_orders.models import RegistrationOrder
from apps.trade_orders.services.purchase_service import (
    create_currency_purchase,
)
from apps.trade_orders.services.shipment_service import (
    create_shipment_part,
)


class InvoiceAPITests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="invoice-test-user",
            password="StrongTestPassword123!",
        )

        self.client.force_authenticate(
            user=self.user,
        )
        self.url = "/api/documents/invoices/"

        self.company = Company.objects.create(
            name="Invoice API Company",
            national_id="2233445566",
            company_type="COMMERCIAL",
        )

        self.order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="INV-API-001",
            registered_amount=Decimal("100000"),
            currency="USD",
        )

        self.purchase = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("40000"),
            currency="USD",
            purchase_date=date(2026, 8, 22),
        )

        self.shipment = create_shipment_part(
            currency_purchase=self.purchase,
            amount=Decimal("40000"),
            shipment_date=date(2026, 9, 1),
            received_date=date(2026, 9, 10),
            reference_number="INV-SHIP-001",
        )

    def test_invoice_can_be_created(self):
        payload = {
            "shipment_part": str(self.shipment.id),
            "fob_amount": "38000",
            "freight_amount": "2000",
            "submission_date": "2026-09-15",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["total_amount"],
            "40000.0000",
        )

        self.assertEqual(
            response.data["order_number"],
            "INV-API-001",
        )

        self.assertEqual(
            response.data["company_name"],
            "Invoice API Company",
        )

        self.assertEqual(
            response.data["order_currency"],
            "USD",
        )

    def test_invoice_with_zero_freight_is_allowed(self):
        payload = {
            "shipment_part": str(self.shipment.id),
            "fob_amount": "40000",
            "freight_amount": "0",
            "submission_date": "2026-09-15",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_invoice_total_must_equal_shipment_amount(self):
        payload = {
            "shipment_part": str(self.shipment.id),
            "fob_amount": "38000",
            "freight_amount": "3000",
            "submission_date": "2026-09-15",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_negative_fob_is_rejected(self):
        payload = {
            "shipment_part": str(self.shipment.id),
            "fob_amount": "-1",
            "freight_amount": "40001",
            "submission_date": "2026-09-15",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_negative_freight_is_rejected(self):
        payload = {
            "shipment_part": str(self.shipment.id),
            "fob_amount": "40001",
            "freight_amount": "-1",
            "submission_date": "2026-09-15",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_submission_date_is_returned_in_both_calendars(self):
        payload = {
            "shipment_part": str(self.shipment.id),
            "fob_amount": "40000",
            "freight_amount": "0",
            "submission_date": "2026-09-15",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["submission_date"],
            "2026-09-15",
        )

        self.assertIn(
            "2026/09/15",
            response.data["submission_date_dual"],
        )