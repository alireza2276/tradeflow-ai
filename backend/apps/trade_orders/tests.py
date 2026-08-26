from rest_framework import status
from rest_framework.test import APITestCase

from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

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


class RegistrationOrderAPITests(APITestCase):

    def setUp(self):
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

class PaymentInstrumentAPITests(APITestCase):

    def setUp(self):
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

class CurrencyPurchaseAPITests(APITestCase):

    def setUp(self):
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

class ShipmentPartAPITests(APITestCase):

    def setUp(self):
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