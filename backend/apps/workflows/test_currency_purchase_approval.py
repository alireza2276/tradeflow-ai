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
from apps.workflows.services.approval_service import (
    approve_request,
)
from apps.workflows.services.submission_service import (
    submit_currency_purchase_create,
)


User = get_user_model()


class CurrencyPurchaseApprovalTests(TestCase):
    def setUp(self):
        add_purchase_permission = Permission.objects.get(
            content_type__app_label="trade_orders",
            codename="add_currencypurchase",
        )

        review_permission = Permission.objects.get(
            content_type__app_label="workflows",
            codename="review_approvalrequest",
        )

        self.maker = User.objects.create_user(
            username="approval_maker",
            password="test-password-123",
        )
        self.maker.user_permissions.add(
            add_purchase_permission,
        )

        self.checker = User.objects.create_user(
            username="approval_checker",
            password="test-password-123",
        )
        self.checker.user_permissions.add(
            review_permission,
        )

        self.company = Company.objects.create(
            name="Approval Test Company",
            national_id="9876543210",
            company_type=Company.CompanyType.COMMERCIAL,
        )

        self.registration_order = (
            RegistrationOrder.objects.create(
                company=self.company,
                order_number="RO-APPROVAL-001",
                registered_amount=Decimal("100000.0000"),
                currency="USD",
                is_active=True,
            )
        )

    def test_approval_creates_currency_purchase(self):
        approval_request = submit_currency_purchase_create(
            maker=self.maker,
            registration_order=self.registration_order,
            amount=Decimal("25000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 8),
            reason="Purchase request.",
        )

        self.assertEqual(
            CurrencyPurchase.objects.count(),
            0,
        )

        result = approve_request(
            approval_request=approval_request,
            checker=self.checker,
        )

        self.assertEqual(
            CurrencyPurchase.objects.count(),
            1,
        )

        purchase = CurrencyPurchase.objects.get()

        result.refresh_from_db()

        self.assertEqual(
            result.status,
            ApprovalRequest.Status.APPROVED,
        )
        self.assertEqual(
            result.checker,
            self.checker,
        )
        self.assertEqual(
            result.target_id,
            purchase.pk,
        )

        self.assertEqual(
            purchase.registration_order,
            self.registration_order,
        )
        self.assertEqual(
            purchase.amount,
            Decimal("25000.0000"),
        )
        self.assertEqual(
            purchase.currency,
            "USD",
        )
        self.assertEqual(
            purchase.purchase_date,
            date(2026, 9, 8),
        )

    def test_failed_approval_keeps_request_pending(self):
        approval_request = submit_currency_purchase_create(
            maker=self.maker,
            registration_order=self.registration_order,
            amount=Decimal("80000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 8),
            reason="Large purchase request.",
        )

        CurrencyPurchase.objects.create(
            registration_order=self.registration_order,
            amount=Decimal("30000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 8),
            deadline=date(2027, 3, 8),
        )

        with self.assertRaises(ValidationError):
            approve_request(
                approval_request=approval_request,
                checker=self.checker,
            )

        approval_request.refresh_from_db()

        self.assertEqual(
            approval_request.status,
            ApprovalRequest.Status.PENDING,
        )
        self.assertIsNone(
            approval_request.checker,
        )
        self.assertIsNone(
            approval_request.reviewed_at,
        )
        self.assertIsNone(
            approval_request.target_id,
        )

        self.assertEqual(
            CurrencyPurchase.objects.count(),
            1,
        )

    def test_inactive_order_at_approval_rolls_back(self):
        approval_request = submit_currency_purchase_create(
            maker=self.maker,
            registration_order=self.registration_order,
            amount=Decimal("25000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 8),
        )

        self.registration_order.is_active = False
        self.registration_order.save(
            update_fields=("is_active",)
        )

        with self.assertRaises(ValidationError):
            approve_request(
                approval_request=approval_request,
                checker=self.checker,
            )

        approval_request.refresh_from_db()

        self.assertEqual(
            approval_request.status,
            ApprovalRequest.Status.PENDING,
        )
        self.assertIsNone(
            approval_request.target_id,
        )

        self.assertEqual(
            CurrencyPurchase.objects.count(),
            0,
        )