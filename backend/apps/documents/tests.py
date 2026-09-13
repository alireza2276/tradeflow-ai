from datetime import date
from decimal import Decimal
from threading import Event, Thread

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import close_old_connections
from django.test import TransactionTestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.companies.models import Company
from apps.documents.models import Invoice
from apps.documents.services.invoice_service import (
    create_invoice,
)
from apps.trade_orders.models import (
    RegistrationOrder,
)
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

        invoice_content_type = ContentType.objects.get_for_model(
            Invoice,
        )

        invoice_permissions = Permission.objects.filter(
            content_type=invoice_content_type,
            codename__in=[
                "view_invoice",
                "add_invoice",
                "change_invoice",
            ],
        )

        self.user.user_permissions.add(
            *invoice_permissions,
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

    def test_authenticated_user_without_permissions_cannot_view_invoices(self):
        user = get_user_model().objects.create_user(
            username="invoice-no-permission-user",
            password="StrongTestPass123!",
        )

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_user_with_view_permission_can_view_invoices(self):
        user = get_user_model().objects.create_user(
            username="invoice-viewer-user",
            password="StrongTestPass123!",
        )

        content_type = ContentType.objects.get_for_model(
            Invoice,
        )

        view_permission = Permission.objects.get(
            content_type=content_type,
            codename="view_invoice",
        )

        user.user_permissions.add(view_permission)

        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_invoice_can_be_updated_safely(self):
        invoice = Invoice.objects.create(
            shipment_part=self.shipment,
            fob_amount=Decimal("38000"),
            freight_amount=Decimal("2000"),
            submission_date=date(2026, 9, 15),
        )

        response = self.client.patch(
            f"{self.url}{invoice.id}/",
            {
                "fob_amount": "39000",
                "freight_amount": "1000",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        invoice.refresh_from_db()

        self.assertEqual(
            invoice.fob_amount,
            Decimal("39000"),
        )

        self.assertEqual(
            invoice.freight_amount,
            Decimal("1000"),
        )

        self.assertEqual(
            invoice.total_amount,
            Decimal("40000"),
        )

    def test_invoice_update_rejects_invalid_total(self):
        invoice = Invoice.objects.create(
            shipment_part=self.shipment,
            fob_amount=Decimal("38000"),
            freight_amount=Decimal("2000"),
            submission_date=date(2026, 9, 15),
        )

        response = self.client.patch(
            f"{self.url}{invoice.id}/",
            {
                "fob_amount": "39000",
                "freight_amount": "2000",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        invoice.refresh_from_db()

        self.assertEqual(
            invoice.fob_amount,
            Decimal("38000"),
        )

        self.assertEqual(
            invoice.freight_amount,
            Decimal("2000"),
        )

        self.assertEqual(
            invoice.total_amount,
            Decimal("40000"),
        )

    def test_invoice_shipment_part_cannot_be_changed(self):
        second_order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="INV-API-002",
            registered_amount=Decimal("10000"),
            currency="USD",
        )

        second_purchase = create_currency_purchase(
            registration_order=second_order,
            amount=Decimal("10000"),
            currency="USD",
            purchase_date=date(2026, 8, 23),
        )

        second_shipment = create_shipment_part(
            currency_purchase=second_purchase,
            amount=Decimal("10000"),
            shipment_date=date(2026, 9, 2),
            received_date=date(2026, 9, 11),
            reference_number="INV-SHIP-002",
        )

        invoice = Invoice.objects.create(
            shipment_part=self.shipment,
            fob_amount=Decimal("38000"),
            freight_amount=Decimal("2000"),
            submission_date=date(2026, 9, 15),
        )

        response = self.client.patch(
            f"{self.url}{invoice.id}/",
            {
                "shipment_part": str(second_shipment.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        invoice.refresh_from_db()

        self.assertEqual(
            invoice.shipment_part_id,
            self.shipment.id,
        )

    def test_invoice_delete_is_not_allowed(self):
        invoice = Invoice.objects.create(
            shipment_part=self.shipment,
            fob_amount=Decimal("38000"),
            freight_amount=Decimal("2000"),
            submission_date=date(2026, 9, 15),
        )

        delete_permission = Permission.objects.get(
            content_type=ContentType.objects.get_for_model(
                Invoice,
            ),
            codename="delete_invoice",
        )

        self.user.user_permissions.add(
            delete_permission,
        )

        response = self.client.delete(
            f"{self.url}{invoice.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        self.assertTrue(
            Invoice.objects.filter(
                pk=invoice.pk,
            ).exists()
        )

    def test_invoice_list_returns_document_part_and_running_remaining_amount(self):
        order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="INV-API-REMAINING-001",
            registered_amount=Decimal("100000"),
            currency="EUR",
        )

        purchase = create_currency_purchase(
            registration_order=order,
            amount=Decimal("90000"),
            currency="EUR",
            purchase_date=date(2026, 8, 24),
        )

        first_shipment = create_shipment_part(
            currency_purchase=purchase,
            amount=Decimal("80000"),
            shipment_date=date(2026, 9, 2),
            received_date=date(2026, 9, 11),
            reference_number="INV-REMAINING-SHIP-001",
        )

        second_shipment = create_shipment_part(
            currency_purchase=purchase,
            amount=Decimal("10000"),
            shipment_date=date(2026, 9, 3),
            received_date=date(2026, 9, 12),
            reference_number="INV-REMAINING-SHIP-002",
        )

        first_invoice = Invoice.objects.create(
            shipment_part=first_shipment,
            fob_amount=Decimal("78000"),
            freight_amount=Decimal("2000"),
            submission_date=date(2026, 9, 15),
        )

        second_invoice = Invoice.objects.create(
            shipment_part=second_shipment,
            fob_amount=Decimal("10000"),
            freight_amount=Decimal("0"),
            submission_date=date(2026, 9, 16),
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        invoices_by_id = {
            item["id"]: item
            for item in response.data
        }

        first_data = invoices_by_id[str(first_invoice.id)]
        second_data = invoices_by_id[str(second_invoice.id)]

        self.assertEqual(
            first_data["currency_purchase_amount"],
            "90000.0000",
        )
        self.assertEqual(
            first_data["document_part_number"],
            1,
        )
        self.assertEqual(
            first_data["remaining_amount"],
            "10000.0000",
        )

        self.assertEqual(
            second_data["currency_purchase_amount"],
            "90000.0000",
        )
        self.assertEqual(
            second_data["document_part_number"],
            2,
        )
        self.assertEqual(
            second_data["remaining_amount"],
            "0.0000",
        )


class InvoiceConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.company = Company.objects.create(
            name="Invoice Concurrency Company",
            national_id="7766554433",
            company_type="COMMERCIAL",
        )

        self.order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="INV-CONCURRENT-001",
            registered_amount=Decimal("40000"),
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
            reference_number="INV-CONCURRENT-SHIP-001",
        )

    def test_concurrent_invoice_creation_allows_only_one_invoice(self):
        start = Event()
        errors = []
        results = []

        def create_invoice_worker():
            close_old_connections()

            try:
                if not start.wait(timeout=5):
                    errors.append(
                        "Invoice thread timed out waiting to start."
                    )
                    return

                shipment = type(self.shipment).objects.get(
                    pk=self.shipment.pk
                )

                try:
                    create_invoice(
                        shipment_part=shipment,
                        fob_amount=Decimal("38000"),
                        freight_amount=Decimal("2000"),
                        submission_date=date(2026, 9, 15),
                    )

                    results.append(True)

                except ValidationError:
                    results.append(False)

            except Exception as exc:
                errors.append(str(exc))

            finally:
                close_old_connections()

        first_thread = Thread(
            target=create_invoice_worker
        )

        second_thread = Thread(
            target=create_invoice_worker
        )

        first_thread.start()
        second_thread.start()

        start.set()

        first_thread.join(timeout=10)
        second_thread.join(timeout=10)

        self.assertFalse(
            first_thread.is_alive(),
            "First invoice thread did not finish.",
        )

        self.assertFalse(
            second_thread.is_alive(),
            "Second invoice thread did not finish.",
        )

        self.assertEqual(
            errors,
            [],
        )

        self.assertEqual(
            len(results),
            2,
        )

        self.assertEqual(
            results.count(True),
            1,
            "Exactly one concurrent invoice creation must succeed.",
        )

        self.assertEqual(
            Invoice.objects.filter(
                shipment_part=self.shipment,
            ).count(),
            1,
        )
