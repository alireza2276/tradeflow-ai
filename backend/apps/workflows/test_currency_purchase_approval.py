from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.companies.models import Company
from apps.common.test_regulatory_helpers import ensure_test_regulatory_context

from apps.trade_orders.models import (
    CurrencyPurchase,
    RegistrationOrder,
)

from apps.workflows.models import ApprovalRequest

from apps.workflows.services.approval_service import (
    approve_request,
)

from apps.workflows.services.submission_service import (
    submit_currency_purchase_correction,
    submit_currency_purchase_create,
    submit_currency_purchase_void,
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
        ensure_test_regulatory_context(
            registration_order=self.registration_order,
            issue_date=date(2026, 9, 8),
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

    def test_approval_applies_currency_purchase_correction(self):
        change_permission = Permission.objects.get(
            content_type__app_label="trade_orders",
            codename="change_currencypurchase",
        )
        self.maker.user_permissions.add(
            change_permission,
        )

        purchase = CurrencyPurchase.objects.create(
            registration_order=self.registration_order,
            amount=Decimal("50000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 1),
            deadline=date(2027, 3, 1),
        )

        approval_request = (
            submit_currency_purchase_correction(
                maker=self.maker,
                purchase=purchase,
                amount=Decimal("60000.0000"),
                purchase_date=date(2026, 9, 5),
                reason="Correct amount and purchase date.",
            )
        )

        purchase.refresh_from_db()

        self.assertEqual(
            purchase.amount,
            Decimal("50000.0000"),
        )
        self.assertEqual(
            purchase.purchase_date,
            date(2026, 9, 1),
        )

        result = approve_request(
            approval_request=approval_request,
            checker=self.checker,
        )

        purchase.refresh_from_db()
        result.refresh_from_db()

        self.assertEqual(
            purchase.amount,
            Decimal("60000.0000"),
        )
        self.assertEqual(
            purchase.purchase_date,
            date(2026, 9, 5),
        )

        self.assertEqual(
            purchase.deadline,
            date(2027, 3, 5),
        )

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

    def test_stale_correction_is_rejected_without_modifying_purchase(self):
        change_permission = Permission.objects.get(
            content_type__app_label="trade_orders",
            codename="change_currencypurchase",
        )
        self.maker.user_permissions.add(
            change_permission,
        )

        purchase = CurrencyPurchase.objects.create(
            registration_order=self.registration_order,
            amount=Decimal("50000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 1),
            deadline=date(2027, 3, 1),
        )

        approval_request = (
            submit_currency_purchase_correction(
                maker=self.maker,
                purchase=purchase,
                amount=Decimal("60000.0000"),
                purchase_date=date(2026, 9, 5),
                reason="Correct amount and date.",
            )
        )

        purchase.amount = Decimal("55000.0000")
        purchase.save(
            update_fields=(
                "amount",
                "updated_at",
            )
        )

        with self.assertRaises(ValidationError):
            approve_request(
                approval_request=approval_request,
                checker=self.checker,
            )

        purchase.refresh_from_db()
        approval_request.refresh_from_db()

        self.assertEqual(
            purchase.amount,
            Decimal("55000.0000"),
        )

        self.assertEqual(
            purchase.purchase_date,
            date(2026, 9, 1),
        )

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

    def test_tampered_correction_payload_is_rejected(self):
        change_permission = Permission.objects.get(
            content_type__app_label="trade_orders",
            codename="change_currencypurchase",
        )
        self.maker.user_permissions.add(
            change_permission,
        )

        purchase = CurrencyPurchase.objects.create(
            registration_order=self.registration_order,
            amount=Decimal("50000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 1),
            deadline=date(2027, 3, 1),
        )

        approval_request = (
            submit_currency_purchase_correction(
                maker=self.maker,
                purchase=purchase,
                amount=Decimal("60000.0000"),
                purchase_date=date(2026, 9, 5),
                reason="Correct amount and date.",
            )
        )

        tampered_payload = dict(
            approval_request.payload
        )
        tampered_payload["unexpected_field"] = (
            "tampered"
        )

        approval_request.payload = tampered_payload
        approval_request.save(
            update_fields=("payload",)
        )

        with self.assertRaises(ValidationError):
            approve_request(
                approval_request=approval_request,
                checker=self.checker,
            )

        purchase.refresh_from_db()
        approval_request.refresh_from_db()

        self.assertEqual(
            purchase.amount,
            Decimal("50000.0000"),
        )
        self.assertEqual(
            purchase.purchase_date,
            date(2026, 9, 1),
        )

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

    def test_approval_applies_currency_purchase_void(self):
        void_permission = Permission.objects.get(
            content_type__app_label="trade_orders",
            codename="void_currencypurchase",
        )
        self.maker.user_permissions.add(
            void_permission,
        )

        purchase = CurrencyPurchase.objects.create(
            registration_order=self.registration_order,
            amount=Decimal("50000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 1),
            deadline=date(2027, 3, 1),
        )

        approval_request = submit_currency_purchase_void(
            maker=self.maker,
            purchase=purchase,
            reason="Purchase entered incorrectly.",
        )

        purchase.refresh_from_db()

        self.assertFalse(
            purchase.is_void,
        )

        result = approve_request(
            approval_request=approval_request,
            checker=self.checker,
        )

        purchase.refresh_from_db()
        result.refresh_from_db()

        self.assertTrue(
            purchase.is_void,
        )
        self.assertIsNotNone(
            purchase.voided_at,
        )
        self.assertEqual(
            purchase.voided_by,
            self.checker,
        )
        self.assertEqual(
            purchase.void_reason,
            "Purchase entered incorrectly.",
        )

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

    def test_void_is_rejected_if_shipment_is_added_before_approval(self):
        from apps.trade_orders.models import ShipmentPart

        void_permission = Permission.objects.get(
            content_type__app_label="trade_orders",
            codename="void_currencypurchase",
        )
        self.maker.user_permissions.add(
            void_permission,
        )

        purchase = CurrencyPurchase.objects.create(
            registration_order=self.registration_order,
            amount=Decimal("50000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 1),
            deadline=date(2027, 3, 1),
        )

        approval_request = submit_currency_purchase_void(
            maker=self.maker,
            purchase=purchase,
            reason="Purchase entered incorrectly.",
        )

        ShipmentPart.objects.create(
            currency_purchase=purchase,
            amount=Decimal("10000.0000"),
        )

        with self.assertRaises(ValidationError):
            approve_request(
                approval_request=approval_request,
                checker=self.checker,
            )

        purchase.refresh_from_db()
        approval_request.refresh_from_db()

        self.assertFalse(
            purchase.is_void,
        )
        self.assertIsNone(
            purchase.voided_at,
        )
        self.assertIsNone(
            purchase.voided_by,
        )
        self.assertEqual(
            purchase.void_reason,
            "",
        )

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

    def test_stale_void_is_rejected_without_voiding_purchase(self):
        void_permission = Permission.objects.get(
            content_type__app_label="trade_orders",
            codename="void_currencypurchase",
        )
        self.maker.user_permissions.add(
            void_permission,
        )

        purchase = CurrencyPurchase.objects.create(
            registration_order=self.registration_order,
            amount=Decimal("50000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 1),
            deadline=date(2027, 3, 1),
        )

        approval_request = submit_currency_purchase_void(
            maker=self.maker,
            purchase=purchase,
            reason="Purchase entered incorrectly.",
        )

        purchase.amount = Decimal("55000.0000")
        purchase.save(
            update_fields=(
                "amount",
                "updated_at",
            )
        )

        with self.assertRaises(ValidationError):
            approve_request(
                approval_request=approval_request,
                checker=self.checker,
            )

        purchase.refresh_from_db()
        approval_request.refresh_from_db()

        self.assertEqual(
            purchase.amount,
            Decimal("55000.0000"),
        )
        self.assertFalse(
            purchase.is_void,
        )
        self.assertIsNone(
            purchase.voided_at,
        )
        self.assertIsNone(
            purchase.voided_by,
        )
        self.assertEqual(
            purchase.void_reason,
            "",
        )

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