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

from apps.workflows.services.submission_service import (
    submit_currency_purchase_correction,
    submit_currency_purchase_create,
    submit_currency_purchase_void,
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
        ensure_test_regulatory_context(
            registration_order=self.registration_order,
            issue_date=date(2026, 9, 8),
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

    def test_correction_submission_does_not_modify_purchase(self):
        purchase = CurrencyPurchase.objects.create(
            registration_order=self.registration_order,
            amount=Decimal("50000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 1),
            deadline=date(2027, 3, 1),
        )

        change_permission = Permission.objects.get(
            content_type__app_label="trade_orders",
            codename="change_currencypurchase",
        )

        self.maker.user_permissions.add(
            change_permission,
        )

        approval_request = (
            submit_currency_purchase_correction(
                maker=self.maker,
                purchase=purchase,
                amount=Decimal("60000.0000"),
                purchase_date=date(2026, 9, 5),
                reason="Correct purchase amount and date.",
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

        self.assertEqual(
            approval_request.status,
            ApprovalRequest.Status.PENDING,
        )
        self.assertEqual(
            approval_request.operation,
            ApprovalRequest.Operation.CORRECT,
        )
        self.assertEqual(
            approval_request.target_type,
            "currency_purchase",
        )
        self.assertEqual(
            approval_request.target_id,
            purchase.pk,
        )

        self.assertEqual(
            approval_request.payload["before"]["amount"],
            "50000.0000",
        )
        self.assertEqual(
            approval_request.payload["proposed"]["amount"],
            "60000.0000",
        )
        self.assertEqual(
            approval_request.payload["before"]["purchase_date"],
            "2026-09-01",
        )
        self.assertEqual(
            approval_request.payload["proposed"]["purchase_date"],
            "2026-09-05",
        )
        self.assertEqual(
            approval_request.reason,
            "Correct purchase amount and date.",
        )
        self.assertIn(
            "version",
            approval_request.payload,
        )

    def test_correction_requires_reason(self):
        purchase = CurrencyPurchase.objects.create(
            registration_order=self.registration_order,
            amount=Decimal("50000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 1),
            deadline=date(2027, 3, 1),
        )

        change_permission = Permission.objects.get(
            content_type__app_label="trade_orders",
            codename="change_currencypurchase",
        )
        self.maker.user_permissions.add(change_permission)

        with self.assertRaises(ValidationError):
            submit_currency_purchase_correction(
                maker=self.maker,
                purchase=purchase,
                amount=Decimal("60000.0000"),
                purchase_date=date(2026, 9, 5),
                reason="   ",
            )

        self.assertEqual(
            ApprovalRequest.objects.count(),
            0,
        )

    def test_correction_requires_change_permission(self):
        purchase = CurrencyPurchase.objects.create(
            registration_order=self.registration_order,
            amount=Decimal("50000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 1),
            deadline=date(2027, 3, 1),
        )

        with self.assertRaises(ValidationError):
            submit_currency_purchase_correction(
                maker=self.maker,
                purchase=purchase,
                amount=Decimal("60000.0000"),
                purchase_date=date(2026, 9, 5),
                reason="Correct purchase.",
            )

        self.assertEqual(
            ApprovalRequest.objects.count(),
            0,
        )

    def test_correction_without_actual_change_is_rejected(self):
        purchase = CurrencyPurchase.objects.create(
            registration_order=self.registration_order,
            amount=Decimal("50000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 1),
            deadline=date(2027, 3, 1),
        )

        change_permission = Permission.objects.get(
            content_type__app_label="trade_orders",
            codename="change_currencypurchase",
        )
        self.maker.user_permissions.add(change_permission)

        with self.assertRaises(ValidationError):
            submit_currency_purchase_correction(
                maker=self.maker,
                purchase=purchase,
                amount=Decimal("50000.0000"),
                purchase_date=date(2026, 9, 1),
                reason="No real change.",
            )

        self.assertEqual(
            ApprovalRequest.objects.count(),
            0,
        )

    def test_correction_cannot_reduce_below_shipment_total(self):
        purchase = CurrencyPurchase.objects.create(
            registration_order=self.registration_order,
            amount=Decimal("50000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 1),
            deadline=date(2027, 3, 1),
        )

        change_permission = Permission.objects.get(
            content_type__app_label="trade_orders",
            codename="change_currencypurchase",
        )
        self.maker.user_permissions.add(change_permission)

        from apps.trade_orders.models import ShipmentPart

        ShipmentPart.objects.create(
            currency_purchase=purchase,
            amount=Decimal("40000.0000"),
        )

        with self.assertRaises(ValidationError):
            submit_currency_purchase_correction(
                maker=self.maker,
                purchase=purchase,
                amount=Decimal("30000.0000"),
                purchase_date=date(2026, 9, 5),
                reason="Incorrect reduction.",
            )

        purchase.refresh_from_db()

        self.assertEqual(
            purchase.amount,
            Decimal("50000.0000"),
        )
        self.assertEqual(
            ApprovalRequest.objects.count(),
            0,
        )

    def test_void_submission_creates_pending_request_without_voiding_purchase(self):
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
        self.assertEqual(
            approval_request.operation,
            ApprovalRequest.Operation.VOID,
        )
        self.assertEqual(
            approval_request.target_type,
            "currency_purchase",
        )
        self.assertEqual(
            approval_request.target_id,
            purchase.pk,
        )
        self.assertEqual(
            approval_request.reason,
            "Purchase entered incorrectly.",
        )
        self.assertIn(
            "version",
            approval_request.payload,
        )

    def test_void_requires_reason(self):
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

        with self.assertRaises(ValidationError):
            submit_currency_purchase_void(
                maker=self.maker,
                purchase=purchase,
                reason="   ",
            )

        self.assertFalse(
            ApprovalRequest.objects.exists()
        )

        purchase.refresh_from_db()

        self.assertFalse(
            purchase.is_void,
        )

    def test_void_requires_permission(self):
        purchase = CurrencyPurchase.objects.create(
            registration_order=self.registration_order,
            amount=Decimal("50000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 1),
            deadline=date(2027, 3, 1),
        )

        with self.assertRaises(ValidationError):
            submit_currency_purchase_void(
                maker=self.maker,
                purchase=purchase,
                reason="Purchase entered incorrectly.",
            )

        self.assertFalse(
            ApprovalRequest.objects.exists()
        )

        purchase.refresh_from_db()

        self.assertFalse(
            purchase.is_void,
        )

    def test_void_with_shipment_part_is_rejected(self):
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

        ShipmentPart.objects.create(
            currency_purchase=purchase,
            amount=Decimal("10000.0000"),
        )

        with self.assertRaises(ValidationError):
            submit_currency_purchase_void(
                maker=self.maker,
                purchase=purchase,
                reason="Attempt to void purchase with shipment.",
            )

        purchase.refresh_from_db()

        self.assertFalse(
            purchase.is_void,
        )

        self.assertEqual(
            ApprovalRequest.objects.count(),
            0,
        )

    def test_already_void_purchase_cannot_be_submitted_for_void(self):
        from django.utils import timezone

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
            is_void=True,
            voided_at=timezone.now(),
            voided_by=self.maker,
            void_reason="Previously voided.",
        )

        with self.assertRaises(ValidationError):
            submit_currency_purchase_void(
                maker=self.maker,
                purchase=purchase,
                reason="Try to void again.",
            )

        self.assertEqual(
            ApprovalRequest.objects.count(),
            0,
        )