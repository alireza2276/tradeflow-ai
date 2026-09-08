from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.companies.models import Company
from apps.trade_orders.models import (
    CurrencyPurchase,
    RegistrationOrder,
)
from apps.workflows.models import ApprovalRequest
from apps.workflows.services.submission_service import (
    submit_currency_purchase_create,
)


User = get_user_model()


class CurrencyPurchaseSubmissionTests(TestCase):
    def setUp(self):
        self.maker = User.objects.create_user(
            username="purchase_maker",
            password="test-password-123",
        )

        add_purchase_permission = Permission.objects.get(
            content_type__app_label="trade_orders",
            codename="add_currencypurchase",
        )

        self.maker.user_permissions.add(
            add_purchase_permission,
        )

        self.company = Company.objects.create(
            name="Test Trading Company",
            national_id="1234567890",
            company_type=Company.CompanyType.COMMERCIAL,
        )

        self.registration_order = (
            RegistrationOrder.objects.create(
                company=self.company,
                order_number="RO-TEST-001",
                registered_amount=Decimal("100000.0000"),
                currency="USD",
                is_active=True,
            )
        )

    def test_submission_creates_pending_request_not_purchase(self):
        approval_request = submit_currency_purchase_create(
            maker=self.maker,
            registration_order=self.registration_order,
            amount=Decimal("25000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 8),
            reason="New currency purchase.",
        )

        self.assertEqual(
            CurrencyPurchase.objects.count(),
            0,
        )

        self.assertEqual(
            ApprovalRequest.objects.count(),
            1,
        )

        self.assertEqual(
            approval_request.status,
            ApprovalRequest.Status.PENDING,
        )

        self.assertEqual(
            approval_request.operation,
            ApprovalRequest.Operation.CREATE,
        )

        self.assertEqual(
            approval_request.target_type,
            "currency_purchase",
        )

        self.assertIsNone(
            approval_request.target_id,
        )

        self.assertEqual(
            approval_request.maker,
            self.maker,
        )

        self.assertEqual(
            approval_request.payload[
                "registration_order_id"
            ],
            str(self.registration_order.pk),
        )

        self.assertEqual(
            approval_request.payload["amount"],
            "25000.0000",
        )

        self.assertEqual(
            approval_request.payload["currency"],
            "USD",
        )

        self.assertEqual(
            approval_request.payload["purchase_date"],
            "2026-09-08",
        )

    def test_user_without_permission_cannot_submit(self):
        unauthorized_user = User.objects.create_user(
            username="unauthorized_user",
            password="test-password-123",
        )

        with self.assertRaises(ValidationError):
            submit_currency_purchase_create(
                maker=unauthorized_user,
                registration_order=self.registration_order,
                amount=Decimal("25000.0000"),
                currency="USD",
                purchase_date=date(2026, 9, 8),
            )

        self.assertEqual(
            ApprovalRequest.objects.count(),
            0,
        )

        self.assertEqual(
            CurrencyPurchase.objects.count(),
            0,
        )

    def test_currency_mismatch_is_rejected(self):
        with self.assertRaises(ValidationError):
            submit_currency_purchase_create(
                maker=self.maker,
                registration_order=self.registration_order,
                amount=Decimal("25000.0000"),
                currency="EUR",
                purchase_date=date(2026, 9, 8),
            )

        self.assertEqual(
            ApprovalRequest.objects.count(),
            0,
        )

        self.assertEqual(
            CurrencyPurchase.objects.count(),
            0,
        )

    def test_inactive_registration_order_is_rejected(self):
        self.registration_order.is_active = False
        self.registration_order.save(
            update_fields=("is_active",)
        )

        with self.assertRaises(ValidationError):
            submit_currency_purchase_create(
                maker=self.maker,
                registration_order=self.registration_order,
                amount=Decimal("25000.0000"),
                currency="USD",
                purchase_date=date(2026, 9, 8),
            )

        self.assertEqual(
            ApprovalRequest.objects.count(),
            0,
        )

        self.assertEqual(
            CurrencyPurchase.objects.count(),
            0,
        )

    def test_amount_exceeding_registration_order_is_rejected(self):
        CurrencyPurchase.objects.create(
            registration_order=self.registration_order,
            amount=Decimal("70000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 1),
            deadline=date(2027, 3, 1),
        )

        with self.assertRaises(ValidationError):
            submit_currency_purchase_create(
                maker=self.maker,
                registration_order=self.registration_order,
                amount=Decimal("40000.0000"),
                currency="USD",
                purchase_date=date(2026, 9, 8),
            )

        self.assertEqual(
            ApprovalRequest.objects.count(),
            0,
        )

        self.assertEqual(
            CurrencyPurchase.objects.count(),
            1,
        )