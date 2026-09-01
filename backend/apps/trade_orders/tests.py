from threading import Event, Thread

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from django.db import close_old_connections, transaction

from django.test import TransactionTestCase
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.db.models import Sum
from apps.companies.models import Company
from apps.documents.services.invoice_service import create_invoice
from apps.trade_orders.models import RegistrationOrder
from apps.trade_orders.services.deadline_service import (
    DeadlineStatus,
    calculate_purchase_deadline,
    get_deadline_status,
)
from apps.trade_orders.services.purchase_service import (
    create_currency_purchase,
)
from apps.trade_orders.services.shipment_service import (
    create_shipment_part,
)

from apps.trade_orders.services.payment_instrument_service import (
    create_payment_instrument,
)

from apps.trade_orders.services.balance_service import (
    get_purchase_balance,
)

from apps.trade_orders.models import (
    CurrencyPurchase,
    PaymentInstrument,
    RegistrationOrder,
    ShipmentPart,
)

from django.test import TestCase

from apps.trade_orders.services.dashboard_service import (
    get_dashboard_summary,
)

class PaymentInstrumentServiceTests(TestCase):

    def setUp(self):
        self.company = Company.objects.create(
            name="Payment Test Company",
            national_id="5566778899",
            company_type="COMMERCIAL",
        )

        self.order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="PAY-001",
            registered_amount=Decimal("100000"),
            currency="USD",
        )

    def test_payment_instrument_can_be_created(self):
        instrument = create_payment_instrument(
            registration_order=self.order,
            instrument_number="PI-123456",
        )

        self.assertEqual(
            instrument.instrument_number,
            "PI-123456",
        )

    def test_registration_order_can_have_only_one_payment_instrument(self):
        create_payment_instrument(
            registration_order=self.order,
            instrument_number="PI-123456",
        )

        with self.assertRaises(ValidationError):
            create_payment_instrument(
                registration_order=self.order,
                instrument_number="PI-654321",
            )

    def test_payment_instrument_number_must_be_unique(self):
        create_payment_instrument(
            registration_order=self.order,
            instrument_number="PI-123456",
        )

        second_order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="PAY-002",
            registered_amount=Decimal("50000"),
            currency="USD",
        )

        with self.assertRaises(ValidationError):
            create_payment_instrument(
                registration_order=second_order,
                instrument_number="PI-123456",
            )

    def test_empty_payment_instrument_number_is_rejected(self):
        with self.assertRaises(ValidationError):
            create_payment_instrument(
                registration_order=self.order,
                instrument_number="   ",
            )


class PurchaseServiceTests(TestCase):

    def setUp(self):
        self.company = Company.objects.create(
            name="Test Company",
            national_id="1234567890",
            company_type="COMMERCIAL",
        )

        self.order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="TEST-001",
            registered_amount=Decimal("100000"),
            currency="USD",
        )

    def test_purchase_within_order_limit_is_allowed(self):
        purchase = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("60000"),
            currency="USD",
            purchase_date=date(2026, 8, 22),
        )

        self.assertEqual(
            purchase.amount,
            Decimal("60000"),
        )

    def test_total_purchases_cannot_exceed_order_amount(self):
        create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("60000"),
            currency="USD",
            purchase_date=date(2026, 8, 22),
        )

        create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("40000"),
            currency="USD",
            purchase_date=date(2026, 8, 22),
        )

        with self.assertRaises(ValidationError):
            create_currency_purchase(
                registration_order=self.order,
                amount=Decimal("1"),
                currency="USD",
                purchase_date=date(2026, 8, 22),
            )

    def test_zero_purchase_is_rejected(self):
        with self.assertRaises(ValidationError):
            create_currency_purchase(
                registration_order=self.order,
                amount=Decimal("0"),
                currency="USD",
                purchase_date=date(2026, 8, 22),
            )

    def test_negative_purchase_is_rejected(self):
        with self.assertRaises(ValidationError):
            create_currency_purchase(
                registration_order=self.order,
                amount=Decimal("-100"),
                currency="USD",
                purchase_date=date(2026, 8, 22),
            )

    def test_deadline_is_calculated_automatically(self):
        purchase = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("60000"),
            currency="USD",
            purchase_date=date(2026, 8, 22),
        )

        self.assertEqual(
            purchase.deadline,
            date(2027, 2, 22),
        )


class ShipmentServiceTests(TestCase):

    def setUp(self):
        self.company = Company.objects.create(
            name="Shipment Test Company",
            national_id="9876543210",
            company_type="COMMERCIAL",
        )

        self.order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="SHIP-001",
            registered_amount=Decimal("100000"),
            currency="USD",
        )

        self.purchase = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("40000"),
            currency="USD",
            purchase_date=date(2026, 8, 22),
        )

    def test_shipment_parts_within_purchase_limit_are_allowed(self):
        create_shipment_part(
            currency_purchase=self.purchase,
            amount=Decimal("15000"),
        )

        create_shipment_part(
            currency_purchase=self.purchase,
            amount=Decimal("25000"),
        )

        self.assertEqual(
            self.purchase.shipment_parts.count(),
            2,
        )

    def test_shipment_parts_cannot_exceed_purchase_amount(self):
        create_shipment_part(
            currency_purchase=self.purchase,
            amount=Decimal("30000"),
        )

        with self.assertRaises(ValidationError):
            create_shipment_part(
                currency_purchase=self.purchase,
                amount=Decimal("10001"),
            )

    def test_zero_shipment_is_rejected(self):
        with self.assertRaises(ValidationError):
            create_shipment_part(
                currency_purchase=self.purchase,
                amount=Decimal("0"),
            )

    def test_negative_shipment_is_rejected(self):
        with self.assertRaises(ValidationError):
            create_shipment_part(
                currency_purchase=self.purchase,
                amount=Decimal("-100"),
            )

    def test_shipment_parts_cannot_exceed_remaining_purchase_amount(self):
        create_shipment_part(
            currency_purchase=self.purchase,
            amount=Decimal("25000"),
        )

        with self.assertRaises(ValidationError):
            create_shipment_part(
                currency_purchase=self.purchase,
                amount=Decimal("15001"),
            )

    def test_purchase_balance_with_one_shipment_part(self):
        create_shipment_part(
            currency_purchase=self.purchase,
            amount=Decimal("20000"),
        )

        balance = get_purchase_balance(
            purchase=self.purchase,
        )

        self.assertEqual(
            balance["purchase_amount"],
            Decimal("40000"),
        )

        self.assertEqual(
            balance["documented_amount"],
            Decimal("20000"),
        )

        self.assertEqual(
            balance["remaining_amount"],
            Decimal("20000"),
        )

    def test_purchase_balance_with_multiple_shipment_parts(self):
        create_shipment_part(
            currency_purchase=self.purchase,
            amount=Decimal("20000"),
        )

        create_shipment_part(
            currency_purchase=self.purchase,
            amount=Decimal("12000"),
        )

        balance = get_purchase_balance(
            purchase=self.purchase,
        )

        self.assertEqual(
            balance["purchase_amount"],
            Decimal("40000"),
        )

        self.assertEqual(
            balance["documented_amount"],
            Decimal("32000"),
        )

        self.assertEqual(
            balance["remaining_amount"],
            Decimal("8000"),
        )

    def test_purchase_balance_becomes_zero_when_fully_documented(self):
        create_shipment_part(
            currency_purchase=self.purchase,
            amount=Decimal("20000"),
        )

        create_shipment_part(
            currency_purchase=self.purchase,
            amount=Decimal("20000"),
        )

        balance = get_purchase_balance(
            purchase=self.purchase,
        )

        self.assertEqual(
            balance["remaining_amount"],
            Decimal("0"),
        )


class InvoiceServiceTests(TestCase):

    def setUp(self):
        self.company = Company.objects.create(
            name="Invoice Test Company",
            national_id="1122334455",
            company_type="COMMERCIAL",
        )

        self.order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="INV-001",
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
        )

    def test_invoice_with_zero_freight_is_valid(self):
        invoice = create_invoice(
            shipment_part=self.shipment,
            fob_amount=Decimal("40000"),
            freight_amount=Decimal("0"),
            submission_date=date(2026, 9, 1),
        )

        self.assertEqual(
            invoice.total_amount,
            Decimal("40000"),
        )

    def test_invoice_with_fob_and_freight_is_valid(self):
        invoice = create_invoice(
            shipment_part=self.shipment,
            fob_amount=Decimal("38000"),
            freight_amount=Decimal("2000"),
            submission_date=date(2026, 9, 1),
        )

        self.assertEqual(
            invoice.total_amount,
            Decimal("40000"),
        )

    def test_invoice_total_is_calculated_from_fob_and_freight(self):
        invoice = create_invoice(
            shipment_part=self.shipment,
            fob_amount=Decimal("38000"),
            freight_amount=Decimal("2000"),
            submission_date=date(2026, 9, 1),
        )

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

    def test_invoice_total_cannot_differ_from_shipment_amount(self):
        with self.assertRaises(ValidationError):
            create_invoice(
                shipment_part=self.shipment,
                fob_amount=Decimal("38000"),
                freight_amount=Decimal("3000"),
                submission_date=date(2026, 9, 1),
            )

    def test_negative_fob_is_rejected(self):
        with self.assertRaises(ValidationError):
            create_invoice(
                shipment_part=self.shipment,
                fob_amount=Decimal("-1"),
                freight_amount=Decimal("40001"),
                submission_date=date(2026, 9, 1),
            )

    def test_negative_freight_is_rejected(self):
        with self.assertRaises(ValidationError):
            create_invoice(
                shipment_part=self.shipment,
                fob_amount=Decimal("40000"),
                freight_amount=Decimal("-1"),
                submission_date=date(2026, 9, 1),
            )

    def test_invoice_total_must_equal_shipment_part_amount(self):
        with self.assertRaises(ValidationError):
            create_invoice(
                shipment_part=self.shipment,
                fob_amount=Decimal("38000"),
                freight_amount=Decimal("3000"),
                submission_date=date(2026, 9, 1),
            )


class DeadlineServiceTests(TestCase):

    def test_commercial_company_gets_six_month_deadline(self):
        deadline = calculate_purchase_deadline(
            purchase_date=date(2026, 8, 22),
            company_type="COMMERCIAL",
        )

        self.assertEqual(
            deadline,
            date(2027, 2, 22),
        )

    def test_production_company_gets_nine_month_deadline(self):
        deadline = calculate_purchase_deadline(
            purchase_date=date(2026, 8, 22),
            company_type="PRODUCTION",
        )

        self.assertEqual(
            deadline,
            date(2027, 5, 22),
        )

    def test_invalid_company_type_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_purchase_deadline(
                purchase_date=date(2026, 8, 22),
                company_type="UNKNOWN",
            )

    def test_end_of_month_is_handled_correctly(self):
        deadline = calculate_purchase_deadline(
            purchase_date=date(2026, 8, 31),
            company_type="COMMERCIAL",
        )

        self.assertEqual(
            deadline,
            date(2027, 2, 28),
        )

class DeadlineStatusTests(TestCase):

    def test_ninety_days_before_deadline(self):
        deadline = date(2027, 2, 22)

        status = get_deadline_status(
            deadline=deadline,
            remaining_amount=Decimal("10000"),
            today=deadline - timedelta(days=90),
        )

        self.assertEqual(
            status,
            DeadlineStatus.NINETY_DAYS,
        )

    def test_sixty_days_before_deadline(self):
        deadline = date(2027, 2, 22)

        status = get_deadline_status(
            deadline=deadline,
            remaining_amount=Decimal("10000"),
            today=deadline - timedelta(days=60),
        )

        self.assertEqual(
            status,
            DeadlineStatus.SIXTY_DAYS,
        )

    def test_thirty_days_before_deadline(self):
        deadline = date(2027, 2, 22)

        status = get_deadline_status(
            deadline=deadline,
            remaining_amount=Decimal("10000"),
            today=deadline - timedelta(days=30),
        )

        self.assertEqual(
            status,
            DeadlineStatus.THIRTY_DAYS,
        )

    def test_twenty_days_before_deadline(self):
        deadline = date(2027, 2, 22)

        status = get_deadline_status(
            deadline=deadline,
            remaining_amount=Decimal("10000"),
            today=deadline - timedelta(days=20),
        )

        self.assertEqual(
            status,
            DeadlineStatus.TWENTY_DAYS,
        )

    def test_ten_days_before_deadline(self):
        deadline = date(2027, 2, 22)

        status = get_deadline_status(
            deadline=deadline,
            remaining_amount=Decimal("10000"),
            today=deadline - timedelta(days=10),
        )

        self.assertEqual(
            status,
            DeadlineStatus.TEN_DAYS,
        )

    def test_five_days_before_deadline(self):
        deadline = date(2027, 2, 22)

        status = get_deadline_status(
            deadline=deadline,
            remaining_amount=Decimal("10000"),
            today=deadline - timedelta(days=5),
        )

        self.assertEqual(
            status,
            DeadlineStatus.FIVE_DAYS,
        )

    def test_last_day(self):
        deadline = date(2027, 2, 22)

        status = get_deadline_status(
            deadline=deadline,
            remaining_amount=Decimal("10000"),
            today=deadline,
        )

        self.assertEqual(
            status,
            DeadlineStatus.LAST_DAY,
        )

    def test_overdue(self):
        deadline = date(2027, 2, 22)

        status = get_deadline_status(
            deadline=deadline,
            remaining_amount=Decimal("10000"),
            today=deadline + timedelta(days=1),
        )

        self.assertEqual(
            status,
            DeadlineStatus.OVERDUE,
        )

    def test_completed_purchase_has_no_warning(self):
        deadline = date(2027, 2, 22)

        status = get_deadline_status(
            deadline=deadline,
            remaining_amount=Decimal("0"),
            today=deadline - timedelta(days=30),
        )

        self.assertEqual(
            status,
            DeadlineStatus.COMPLETED,
        )


class AuthenticatedAPITestCase(APITestCase):

    def authenticate_test_user(self, username):
        self.user = get_user_model().objects.create_user(
            username=username,
            password="StrongTestPassword123!",
        )

        self.client.force_authenticate(
            user=self.user,
        )


class RegistrationOrderAPITests(AuthenticatedAPITestCase):

    def setUp(self):
        self.authenticate_test_user("registration-order-test-user")
        self.url = "/api/trade/registration-orders/"

        self.company = Company.objects.create(
            name="API Test Company",
            national_id="4455667788",
            company_type="COMMERCIAL",
        )

        self.order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="API-ORDER-001",
            registered_amount=Decimal("100000"),
            currency="USD",
        )

    def test_registration_order_list_returns_success(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["company_name"],
            "API Test Company",
        )

    def test_registration_order_can_be_created(self):
        payload = {
            "company": str(self.company.id),
            "order_number": "API-ORDER-002",
            "registered_amount": "50000",
            "currency": "EUR",
            "is_active": True,
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

        self.assertTrue(
            RegistrationOrder.objects.filter(
                company=self.company,
                order_number="API-ORDER-002",
            ).exists()
        )

    def test_duplicate_order_number_for_same_company_is_rejected(self):
        payload = {
            "company": str(self.company.id),
            "order_number": "API-ORDER-001",
            "registered_amount": "50000",
            "currency": "USD",
            "is_active": True,
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

    def test_zero_registered_amount_is_rejected(self):
        payload = {
            "company": str(self.company.id),
            "order_number": "API-ORDER-ZERO",
            "registered_amount": "0",
            "currency": "USD",
            "is_active": True,
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

        self.assertFalse(
            RegistrationOrder.objects.filter(
                order_number="API-ORDER-ZERO",
            ).exists()
        )

    def test_invalid_currency_is_rejected(self):
        payload = {
            "company": str(self.company.id),
            "order_number": "API-ORDER-CURRENCY",
            "registered_amount": "50000",
            "currency": "USDD",
            "is_active": True,
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

        self.assertFalse(
            RegistrationOrder.objects.filter(
                order_number="API-ORDER-CURRENCY",
            ).exists()
        )

    def test_registration_order_without_dependencies_can_be_deleted(self):
        response = self.client.delete(
            f"{self.url}{self.order.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            RegistrationOrder.objects.filter(
                id=self.order.id,
            ).exists()
        )

    def test_registration_order_with_payment_instrument_is_protected(self):
        create_payment_instrument(
            registration_order=self.order,
            instrument_number="PI-PROTECT-001",
        )

        response = self.client.delete(
            f"{self.url}{self.order.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT,
        )

        self.assertEqual(
            response.data["detail"],
            (
                "This registration order cannot be deleted "
                "because it has related payment instruments "
                "or currency purchases."
            ),
        )

        self.assertTrue(
            RegistrationOrder.objects.filter(
                id=self.order.id,
            ).exists()
        )

    def test_registration_order_with_currency_purchase_is_protected(self):
        create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("40000"),
            currency="USD",
            purchase_date=date(2026, 8, 22),
        )

        response = self.client.delete(
            f"{self.url}{self.order.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT,
        )

        self.assertEqual(
            response.data["detail"],
            (
                "This registration order cannot be deleted "
                "because it has related payment instruments "
                "or currency purchases."
            ),
        )

        self.assertTrue(
            RegistrationOrder.objects.filter(
                id=self.order.id,
            ).exists()
        )

    def test_registered_amount_cannot_be_lower_than_total_purchases(self):
        create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("40000"),
            currency="USD",
            purchase_date=date(2026, 8, 22),
        )

        payload = {
            "company": str(self.company.id),
            "order_number": self.order.order_number,
            "registered_amount": "39999",
            "currency": "USD",
            "is_active": True,
        }

        response = self.client.put(
            f"{self.url}{self.order.id}/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.registered_amount,
            Decimal("100000"),
        )

    def test_registration_order_can_be_partially_updated(self):
        response = self.client.patch(
            f"{self.url}{self.order.id}/",
            {
                "registered_amount": "120000",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.registered_amount,
            Decimal("120000"),
        )

    def test_currency_cannot_be_changed_when_purchases_exist(self):
        create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("40000"),
            currency="USD",
            purchase_date=date(2026, 8, 22),
        )

        payload = {
            "company": str(self.company.id),
            "order_number": self.order.order_number,
            "registered_amount": "100000",
            "currency": "EUR",
            "is_active": True,
        }

        response = self.client.put(
            f"{self.url}{self.order.id}/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.currency,
            "USD",
        )

class PaymentInstrumentAPITests(AuthenticatedAPITestCase):
    def setUp(self):
        self.authenticate_test_user("payment-instrument-test-user")
        self.url = "/api/trade/payment-instruments/"

        self.company = Company.objects.create(
            name="Payment API Company",
            national_id="6677889900",
            company_type="COMMERCIAL",
        )

        self.order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="PAY-API-001",
            registered_amount=Decimal("100000"),
            currency="USD",
        )

    def test_payment_instrument_can_be_created(self):
        payload = {
            "registration_order": str(self.order.id),
            "instrument_number": "PI-API-001",
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

        self.assertTrue(
            PaymentInstrument.objects.filter(
                registration_order=self.order,
                instrument_number="PI-API-001",
            ).exists()
        )

        self.assertEqual(
            response.data["order_number"],
            "PAY-API-001",
        )

        self.assertEqual(
            response.data["company_name"],
            "Payment API Company",
        )

    def test_second_payment_instrument_for_same_order_is_rejected(self):
        create_payment_instrument(
            registration_order=self.order,
            instrument_number="PI-API-001",
        )

        payload = {
            "registration_order": str(self.order.id),
            "instrument_number": "PI-API-002",
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

    def test_duplicate_instrument_number_is_rejected(self):
        create_payment_instrument(
            registration_order=self.order,
            instrument_number="PI-API-001",
        )

        second_order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="PAY-API-002",
            registered_amount=Decimal("50000"),
            currency="USD",
        )

        payload = {
            "registration_order": str(second_order.id),
            "instrument_number": "PI-API-001",
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

class CurrencyPurchaseAPITests(AuthenticatedAPITestCase):
    def setUp(self):
        self.authenticate_test_user("currency-purchase-test-user")
        self.url = "/api/trade/currency-purchases/"

        self.company = Company.objects.create(
            name="Purchase API Company",
            national_id="7788990011",
            company_type="COMMERCIAL",
        )

        self.order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="PURCHASE-API-001",
            registered_amount=Decimal("100000"),
            currency="USD",
        )

    def test_currency_purchase_can_be_created(self):
        payload = {
            "registration_order": str(self.order.id),
            "amount": "40000",
            "currency": "USD",
            "purchase_date": "2026-08-22",
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
            response.data["amount"],
            "40000.0000",
        )

        self.assertEqual(
            response.data["deadline"],
            "2027-02-22",
        )

    def test_currency_purchase_cannot_be_created_for_inactive_order(self):
        self.order.is_active = False
        self.order.save(update_fields=["is_active"])

        payload = {
            "registration_order": str(self.order.id),
            "amount": "40000",
            "currency": "USD",
            "purchase_date": "2026-08-22",
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

        self.assertFalse(
            CurrencyPurchase.objects.filter(
                registration_order=self.order,
            ).exists()
        )

    def test_multiple_purchases_up_to_order_amount_are_allowed(self):
        first_payload = {
            "registration_order": str(self.order.id),
            "amount": "40000",
            "currency": "USD",
            "purchase_date": "2026-08-22",
        }

        second_payload = {
            "registration_order": str(self.order.id),
            "amount": "60000",
            "currency": "USD",
            "purchase_date": "2026-08-23",
        }

        first_response = self.client.post(
            self.url,
            first_payload,
            format="json",
        )

        second_response = self.client.post(
            self.url,
            second_payload,
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_total_purchases_cannot_exceed_order_amount(self):
        first_payload = {
            "registration_order": str(self.order.id),
            "amount": "100000",
            "currency": "USD",
            "purchase_date": "2026-08-22",
        }

        self.client.post(
            self.url,
            first_payload,
            format="json",
        )

        second_payload = {
            "registration_order": str(self.order.id),
            "amount": "1",
            "currency": "USD",
            "purchase_date": "2026-08-23",
        }

        response = self.client.post(
            self.url,
            second_payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_zero_purchase_amount_is_rejected(self):
        payload = {
            "registration_order": str(self.order.id),
            "amount": "0",
            "currency": "USD",
            "purchase_date": "2026-08-22",
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

    def test_commercial_deadline_is_six_months(self):
        payload = {
            "registration_order": str(self.order.id),
            "amount": "40000",
            "currency": "USD",
            "purchase_date": "2026-08-22",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.data["deadline"],
            "2027-02-22",
        )

    def test_production_deadline_is_nine_months(self):
        production_company = Company.objects.create(
            name="Production API Company",
            national_id="8899001122",
            company_type="PRODUCTION",
        )

        production_order = RegistrationOrder.objects.create(
            company=production_company,
            order_number="PRODUCTION-API-001",
            registered_amount=Decimal("100000"),
            currency="USD",
        )

        payload = {
            "registration_order": str(production_order.id),
            "amount": "40000",
            "currency": "USD",
            "purchase_date": "2026-08-22",
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
            response.data["deadline"],
            "2027-05-22",
        )

    def test_response_contains_dual_dates(self):
        payload = {
            "registration_order": str(self.order.id),
            "amount": "40000",
            "currency": "USD",
            "purchase_date": "2026-08-22",
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
            response.data["purchase_date_dual"],
            "1405/05/31 (2026/08/22)",
        )

        self.assertEqual(
            response.data["deadline_dual"],
            "1405/12/03 (2027/02/22)",
        )

    def test_purchase_currency_must_match_registration_order_currency(self):
        payload = {
            "registration_order": str(self.order.id),
            "amount": "40000",
            "currency": "EUR",
            "purchase_date": "2026-08-22",
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

        self.assertFalse(
            CurrencyPurchase.objects.filter(
                registration_order=self.order,
            ).exists()
        )

    def test_currency_purchase_amount_can_be_updated(self):
        purchase = CurrencyPurchase.objects.create(
            registration_order=self.order,
            amount=Decimal("40000"),
            currency="USD",
            purchase_date=date(2026, 8, 22),
            deadline=date(2027, 2, 22),
        )

        url = f"{self.url}{purchase.id}/"

        response = self.client.patch(
            url,
            {
                "amount": "50000",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        purchase.refresh_from_db()

        self.assertEqual(
            purchase.amount,
            Decimal("50000"),
        )

    def test_currency_purchase_currency_cannot_be_changed(self):
        purchase = CurrencyPurchase.objects.create(
            registration_order=self.order,
            amount=Decimal("40000"),
            currency="USD",
            purchase_date=date(2026, 8, 22),
            deadline=date(2027, 2, 22),
        )

        url = f"{self.url}{purchase.id}/"

        response = self.client.patch(
            url,
            {
                "currency": "EUR",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        purchase.refresh_from_db()

        self.assertEqual(
            purchase.currency,
            "USD",
        )

    def test_currency_purchase_registration_order_cannot_be_changed(self):
        other_order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="PURCHASE-API-002",
            registered_amount=Decimal("100000"),
            currency="USD",
        )

        purchase = CurrencyPurchase.objects.create(
            registration_order=self.order,
            amount=Decimal("40000"),
            currency="USD",
            purchase_date=date(2026, 8, 22),
            deadline=date(2027, 2, 22),
        )

        url = f"{self.url}{purchase.id}/"

        response = self.client.patch(
            url,
            {
                "registration_order": str(other_order.id),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        purchase.refresh_from_db()

        self.assertEqual(
            purchase.registration_order_id,
            self.order.id,
        )

    def test_currency_purchase_amount_cannot_be_lower_than_total_shipments(self):
        purchase = CurrencyPurchase.objects.create(
            registration_order=self.order,
            amount=Decimal("40000"),
            currency="USD",
            purchase_date=date(2026, 8, 22),
            deadline=date(2027, 2, 22),
        )

        ShipmentPart.objects.create(
            currency_purchase=purchase,
            amount=Decimal("30000"),
            shipment_date=date(2026, 9, 1),
        )

        url = f"{self.url}{purchase.id}/"

        response = self.client.patch(
            url,
            {
                "amount": "20000",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        purchase.refresh_from_db()

        self.assertEqual(
            purchase.amount,
            Decimal("40000"),
        )

    def test_currency_purchase_date_update_recalculates_deadline(self):
        purchase = CurrencyPurchase.objects.create(
            registration_order=self.order,
            amount=Decimal("40000"),
            currency="USD",
            purchase_date=date(2026, 8, 22),
            deadline=date(2027, 2, 22),
        )

        url = f"{self.url}{purchase.id}/"

        response = self.client.patch(
            url,
            {
                "purchase_date": "2026-09-10",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        purchase.refresh_from_db()

        self.assertEqual(
            purchase.purchase_date,
            date(2026, 9, 10),
        )

        self.assertEqual(
            purchase.deadline,
            date(2027, 3, 10),
        )

    def test_currency_purchase_update_cannot_exceed_order_amount(self):
        first_purchase = CurrencyPurchase.objects.create(
            registration_order=self.order,
            amount=Decimal("40000"),
            currency="USD",
            purchase_date=date(2026, 8, 22),
            deadline=date(2027, 2, 22),
        )

        CurrencyPurchase.objects.create(
            registration_order=self.order,
            amount=Decimal("50000"),
            currency="USD",
            purchase_date=date(2026, 8, 23),
            deadline=date(2027, 2, 23),
        )

        url = f"{self.url}{first_purchase.id}/"

        response = self.client.patch(
            url,
            {
                "amount": "60000",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        first_purchase.refresh_from_db()

        self.assertEqual(
            first_purchase.amount,
            Decimal("40000"),
        )


    def test_currency_purchase_cannot_be_deleted(self):
        purchase = CurrencyPurchase.objects.create(
            registration_order=self.order,
            amount=Decimal("40000"),
            currency="USD",
            purchase_date=date(2026, 8, 22),
            deadline=date(2027, 2, 22),
        )

        response = self.client.delete(
            f"{self.url}{purchase.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        self.assertTrue(
            CurrencyPurchase.objects.filter(
                id=purchase.id,
            ).exists()
        )


class ShipmentPartAPITests(AuthenticatedAPITestCase):
    def setUp(self):
        self.authenticate_test_user("shipment-part-test-user")
        self.url = "/api/trade/shipment-parts/"

        self.company = Company.objects.create(
            name="Shipment API Company",
            national_id="9900112233",
            company_type="COMMERCIAL",
        )

        self.order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="SHIP-API-001",
            registered_amount=Decimal("100000"),
            currency="USD",
        )

        self.purchase = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("40000"),
            currency="USD",
            purchase_date=date(2026, 8, 22),
        )

    def test_shipment_part_can_be_created(self):
        payload = {
            "currency_purchase": str(self.purchase.id),
            "amount": "20000",
            "shipment_date": "2026-09-01",
            "received_date": "2026-09-10",
            "reference_number": "SHIP-REF-001",
            "notes": "First shipment part",
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
            response.data["amount"],
            "20000.0000",
        )

        self.assertEqual(
            response.data["reference_number"],
            "SHIP-REF-001",
        )

        self.assertEqual(
            response.data["order_number"],
            "SHIP-API-001",
        )

        self.assertEqual(
            response.data["company_name"],
            "Shipment API Company",
        )

        self.assertEqual(
            response.data["purchase_currency"],
            "USD",
        )

    def test_multiple_shipment_parts_up_to_purchase_amount_are_allowed(self):
        first_payload = {
            "currency_purchase": str(self.purchase.id),
            "amount": "20000",
        }

        second_payload = {
            "currency_purchase": str(self.purchase.id),
            "amount": "20000",
        }

        first_response = self.client.post(
            self.url,
            first_payload,
            format="json",
        )

        second_response = self.client.post(
            self.url,
            second_payload,
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            self.purchase.shipment_parts.count(),
            2,
        )

    def test_shipment_parts_cannot_exceed_purchase_amount(self):
        self.client.post(
            self.url,
            {
                "currency_purchase": str(self.purchase.id),
                "amount": "30000",
            },
            format="json",
        )

        response = self.client.post(
            self.url,
            {
                "currency_purchase": str(self.purchase.id),
                "amount": "10001",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_zero_shipment_amount_is_rejected(self):
        response = self.client.post(
            self.url,
            {
                "currency_purchase": str(self.purchase.id),
                "amount": "0",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_negative_shipment_amount_is_rejected(self):
        response = self.client.post(
            self.url,
            {
                "currency_purchase": str(self.purchase.id),
                "amount": "-100",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_shipment_details_are_saved(self):
        response = self.client.post(
            self.url,
            {
                "currency_purchase": str(self.purchase.id),
                "amount": "10000",
                "shipment_date": "2026-09-01",
                "received_date": "2026-09-10",
                "reference_number": "  SHIP-DETAIL-001  ",
                "notes": "Documents received.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        shipment = ShipmentPart.objects.get(
            currency_purchase=self.purchase,
        )

        self.assertEqual(
            shipment.reference_number,
            "SHIP-DETAIL-001",
        )

        self.assertEqual(
            shipment.shipment_date,
            date(2026, 9, 1),
        )

        self.assertEqual(
            shipment.received_date,
            date(2026, 9, 10),
        )

        self.assertEqual(
            shipment.notes,
            "Documents received.",
        )

class DashboardServiceTests(AuthenticatedAPITestCase):
    def setUp(self):
        self.authenticate_test_user("dashboard-test-user")
        self.company = Company.objects.create(
            name="Dashboard Company",
            national_id="9988776655",
            company_type="COMMERCIAL",
        )

        self.order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="DASH-001",
            registered_amount=Decimal("100000"),
            currency="USD",
        )

    def test_dashboard_summary_counts_active_order_and_purchase(self):
        create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("50000"),
            currency="USD",
            purchase_date=date.today(),
        )

        summary = get_dashboard_summary()

        self.assertEqual(
            summary["active_orders_count"],
            1,
        )

        self.assertEqual(
            summary["active_purchases_count"],
            1,
        )

    def test_dashboard_summary_calculates_currency_totals(self):
        purchase = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("50000"),
            currency="USD",
            purchase_date=date.today(),
        )

        create_shipment_part(
            currency_purchase=purchase,
            amount=Decimal("20000"),
        )

        summary = get_dashboard_summary()

        usd_totals = summary["currency_totals"]["USD"]

        self.assertEqual(
            usd_totals["purchased_amount"],
            Decimal("50000"),
        )

        self.assertEqual(
            usd_totals["documented_amount"],
            Decimal("20000"),
        )

        self.assertEqual(
            usd_totals["remaining_amount"],
            Decimal("30000"),
        )

    def test_dashboard_summary_detects_overdue_purchase(self):
        purchase = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("50000"),
            currency="USD",
            purchase_date=date(2025, 1, 1),
        )

        summary = get_dashboard_summary()

        self.assertEqual(
            summary["overdue_count"],
            1,
        )

    def test_completed_purchase_is_not_counted_as_overdue(self):
        purchase = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("50000"),
            currency="USD",
            purchase_date=date(2025, 1, 1),
        )

        create_shipment_part(
            currency_purchase=purchase,
            amount=Decimal("50000"),
        )

        summary = get_dashboard_summary()

        self.assertEqual(
            summary["overdue_count"],
            0,
        )

        self.assertEqual(
            summary["currency_totals"]["USD"]["remaining_amount"],
            Decimal("0"),
        )

    def test_dashboard_keeps_currency_totals_separate(self):
        usd_purchase = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("50000"),
            currency="USD",
            purchase_date=date.today(),
        )

        create_shipment_part(
            currency_purchase=usd_purchase,
            amount=Decimal("20000"),
        )

        eur_order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="DASH-EUR-001",
            registered_amount=Decimal("80000"),
            currency="EUR",
        )

        eur_purchase = create_currency_purchase(
            registration_order=eur_order,
            amount=Decimal("40000"),
            currency="EUR",
            purchase_date=date.today(),
        )

        create_shipment_part(
            currency_purchase=eur_purchase,
            amount=Decimal("10000"),
        )

        summary = get_dashboard_summary()

        self.assertEqual(
            summary["currency_totals"]["USD"]["purchased_amount"],
            Decimal("50000"),
        )

        self.assertEqual(
            summary["currency_totals"]["USD"]["documented_amount"],
            Decimal("20000"),
        )

        self.assertEqual(
            summary["currency_totals"]["USD"]["remaining_amount"],
            Decimal("30000"),
        )

        self.assertEqual(
            summary["currency_totals"]["EUR"]["purchased_amount"],
            Decimal("40000"),
        )

        self.assertEqual(
            summary["currency_totals"]["EUR"]["documented_amount"],
            Decimal("10000"),
        )

        self.assertEqual(
            summary["currency_totals"]["EUR"]["remaining_amount"],
            Decimal("30000"),
        )

    def test_dashboard_api_returns_summary(self):
        purchase = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("50000"),
            currency="USD",
            purchase_date=date.today(),
        )

        create_shipment_part(
            currency_purchase=purchase,
            amount=Decimal("20000"),
        )

        response = self.client.get(
            "/api/trade/dashboard/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["active_orders_count"],
            1,
        )

        self.assertEqual(
            response.data["active_purchases_count"],
            1,
        )

        self.assertEqual(
            Decimal(
                response.data["currency_totals"]["USD"]["purchased_amount"]
            ),
            Decimal("50000"),
        )

        self.assertEqual(
            Decimal(
                response.data["currency_totals"]["USD"]["documented_amount"]
            ),
            Decimal("20000"),
        )

        self.assertEqual(
            Decimal(
                response.data["currency_totals"]["USD"]["remaining_amount"]
            ),
            Decimal("30000"),
        )

    def test_dashboard_returns_attention_cases(self):
        overdue_purchase = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("50000"),
            currency="USD",
            purchase_date=date(2025, 1, 1),
        )

        due_soon_order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="DASH-DUE-001",
            registered_amount=Decimal("70000"),
            currency="USD",
        )

        due_soon_purchase = create_currency_purchase(
            registration_order=due_soon_order,
            amount=Decimal("30000"),
            currency="USD",
            purchase_date=date.today(),
        )

        due_soon_purchase.deadline = date.today() + timedelta(days=10)
        due_soon_purchase.save(update_fields=["deadline"])

        completed_order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="DASH-COMPLETE-001",
            registered_amount=Decimal("60000"),
            currency="USD",
        )

        completed_purchase = create_currency_purchase(
            registration_order=completed_order,
            amount=Decimal("20000"),
            currency="USD",
            purchase_date=date(2025, 1, 1),
        )

        create_shipment_part(
            currency_purchase=completed_purchase,
            amount=Decimal("20000"),
        )

        summary = get_dashboard_summary()

        attention_cases = summary["attention_cases"]

        self.assertEqual(
            len(attention_cases),
            2,
        )

        statuses = {
            case["status"]
            for case in attention_cases
        }

        self.assertIn(
            "OVERDUE",
            statuses,
        )

        self.assertIn(
            "DUE_SOON",
            statuses,
        )

        purchase_ids = {
            case["purchase_id"]
            for case in attention_cases
        }

        self.assertIn(
            str(overdue_purchase.id),
            purchase_ids,
        )

        self.assertIn(
            str(due_soon_purchase.id),
            purchase_ids,
        )

        self.assertNotIn(
            str(completed_purchase.id),
            purchase_ids,
        )

    def test_dashboard_attention_case_includes_dual_deadline(self):
        purchase = create_currency_purchase(
            registration_order=self.order,
            amount=Decimal("50000"),
            currency="USD",
            purchase_date=date.today(),
        )

        purchase.deadline = date.today() + timedelta(days=10)
        purchase.save(update_fields=["deadline"])

        summary = get_dashboard_summary()

        attention_case = next(
            case
            for case in summary["attention_cases"]
            if case["purchase_id"] == str(purchase.id)
        )

        self.assertIn("deadline_dual", attention_case)
        self.assertIn(
            purchase.deadline.strftime("%Y/%m/%d"),
            attention_case["deadline_dual"],
        )

class RegistrationOrderConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.company = Company.objects.create(
            name="Concurrency Test Company",
            national_id="9988776655",
            company_type="COMMERCIAL",
        )

        self.order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="CONCURRENT-ORDER-001",
            registered_amount=Decimal("100000"),
            currency="USD",
        )

        self.user = get_user_model().objects.create_user(
            username="concurrency-user",
            password="StrongTestPass123!",
        )

        self.orders_url = "/api/trade/registration-orders/"

    def test_purchase_and_order_update_preserve_financial_invariant(self):
        start = Event()
        errors = []
        results = {}

        def reduce_registration_order():
            close_old_connections()

            try:
                client = APIClient()
                client.force_authenticate(user=self.user)

                if not start.wait(timeout=5):
                    errors.append(
                        "Order update timed out waiting to start."
                    )
                    return

                response = client.patch(
                    f"{self.orders_url}{self.order.pk}/",
                    {
                        "registered_amount": "50000",
                    },
                    format="json",
                )

                results["order_status"] = response.status_code

            except Exception as exc:
                errors.append(str(exc))

            finally:
                close_old_connections()

        def create_purchase():
            close_old_connections()

            try:
                if not start.wait(timeout=5):
                    errors.append(
                        "Purchase creation timed out waiting to start."
                    )
                    return

                order = RegistrationOrder.objects.get(
                    pk=self.order.pk
                )

                try:
                    create_currency_purchase(
                        registration_order=order,
                        amount=Decimal("60000"),
                        currency="USD",
                        purchase_date=date(2026, 8, 22),
                    )

                    results["purchase_created"] = True

                except ValidationError:
                    results["purchase_created"] = False

            except Exception as exc:
                errors.append(str(exc))

            finally:
                close_old_connections()

        order_thread = Thread(
            target=reduce_registration_order
        )

        purchase_thread = Thread(
            target=create_purchase
        )

        order_thread.start()
        purchase_thread.start()

        start.set()

        order_thread.join(timeout=10)
        purchase_thread.join(timeout=10)

        self.assertFalse(
            order_thread.is_alive(),
            "Registration order thread did not finish.",
        )

        self.assertFalse(
            purchase_thread.is_alive(),
            "Currency purchase thread did not finish.",
        )

        self.assertEqual(errors, [])

        self.assertIn(
            results.get("order_status"),
            (status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST),
        )

        self.assertIn(
            "purchase_created",
            results,
        )

        order_update_succeeded = (
                results["order_status"] == status.HTTP_200_OK
        )

        purchase_succeeded = results["purchase_created"]

        self.assertNotEqual(
            order_update_succeeded,
            purchase_succeeded,
            (
                "Exactly one concurrent financial operation "
                "must succeed."
            ),
        )

        self.order.refresh_from_db()

        total_purchased = (
                self.order.currency_purchases.aggregate(
                    total=Sum("amount")
                )["total"]
                or Decimal("0")
        )

        self.assertLessEqual(
            total_purchased,
            self.order.registered_amount,
            (
                "Financial invariant violated: total currency "
                "purchases exceeded the registration order amount."
            ),
        )

    def test_registration_order_row_lock_blocks_concurrent_update(self):
        lock_acquired = Event()
        release_lock = Event()
        update_finished = Event()

        errors = []

        def hold_order_lock():
            close_old_connections()

            try:
                with transaction.atomic():
                    RegistrationOrder.objects.select_for_update().get(
                        pk=self.order.pk
                    )

                    lock_acquired.set()

                    if not release_lock.wait(timeout=5):
                        errors.append(
                            "Timed out waiting to release row lock."
                        )
            except Exception as exc:
                errors.append(str(exc))
            finally:
                close_old_connections()

        def update_order():
            close_old_connections()

            try:
                if not lock_acquired.wait(timeout=5):
                    errors.append(
                        "Timed out waiting for row lock."
                    )
                    return

                with transaction.atomic():
                    locked_order = (
                        RegistrationOrder.objects
                        .select_for_update()
                        .get(pk=self.order.pk)
                    )

                    locked_order.registered_amount = Decimal(
                        "120000"
                    )

                    locked_order.save(
                        update_fields=["registered_amount"]
                    )

                update_finished.set()

            except Exception as exc:
                errors.append(str(exc))
            finally:
                close_old_connections()

        lock_thread = Thread(target=hold_order_lock)
        update_thread = Thread(target=update_order)

        lock_thread.start()

        self.assertTrue(
            lock_acquired.wait(timeout=5),
            "First transaction did not acquire the row lock.",
        )

        update_thread.start()

        self.assertFalse(
            update_finished.wait(timeout=0.5),
            "Concurrent update was not blocked by the row lock.",
        )

        release_lock.set()

        lock_thread.join(timeout=5)
        update_thread.join(timeout=5)

        self.assertFalse(
            lock_thread.is_alive(),
            "Lock thread did not finish.",
        )

        self.assertFalse(
            update_thread.is_alive(),
            "Update thread did not finish.",
        )

        self.assertEqual(errors, [])

        self.assertTrue(update_finished.is_set())

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.registered_amount,
            Decimal("120000"),
        )

class ShipmentPartConcurrencyTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.company = Company.objects.create(
            name="Shipment Concurrency Company",
            national_id="8877665544",
            company_type="COMMERCIAL",
        )

        self.order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="SHIP-CONCURRENT-001",
            registered_amount=Decimal("100000"),
            currency="USD",
        )

        self.purchase = CurrencyPurchase.objects.create(
            registration_order=self.order,
            amount=Decimal("100000"),
            currency="USD",
            purchase_date=date(2026, 8, 22),
            deadline=date(2027, 2, 22),
        )

    def test_concurrent_shipments_preserve_purchase_amount_invariant(self):
        start = Event()
        errors = []
        results = []

        def create_shipment(amount):
            close_old_connections()

            try:
                if not start.wait(timeout=5):
                    errors.append(
                        "Shipment thread timed out waiting to start."
                    )
                    return

                purchase = CurrencyPurchase.objects.get(
                    pk=self.purchase.pk
                )

                try:
                    create_shipment_part(
                        currency_purchase=purchase,
                        amount=amount,
                        shipment_date=date(2026, 8, 25),
                        reference_number="CONCURRENT-SHIPMENT",
                    )

                    results.append(True)

                except ValidationError:
                    results.append(False)

            except Exception as exc:
                errors.append(str(exc))

            finally:
                close_old_connections()

        first_thread = Thread(
            target=create_shipment,
            args=(Decimal("60000"),),
        )

        second_thread = Thread(
            target=create_shipment,
            args=(Decimal("60000"),),
        )

        first_thread.start()
        second_thread.start()

        start.set()

        first_thread.join(timeout=10)
        second_thread.join(timeout=10)

        self.assertFalse(
            first_thread.is_alive(),
            "First shipment thread did not finish.",
        )

        self.assertFalse(
            second_thread.is_alive(),
            "Second shipment thread did not finish.",
        )

        self.assertEqual(errors, [])

        self.assertEqual(
            len(results),
            2,
        )

        self.assertEqual(
            results.count(True),
            1,
            "Exactly one concurrent shipment must succeed.",
        )

        self.purchase.refresh_from_db()

        total_shipped = sum(
            (
                part.amount
                for part in self.purchase.shipment_parts.all()
            ),
            Decimal("0"),
        )

        self.assertLessEqual(
            total_shipped,
            self.purchase.amount,
            (
                "Financial invariant violated: total shipment "
                "amount exceeded the currency purchase amount."
            ),
        )