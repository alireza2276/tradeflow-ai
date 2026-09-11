from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from datetime import date
from decimal import Decimal

from apps.companies.models import Company
from apps.trade_orders.models import (
    CurrencyPurchase,
    RegistrationOrder,
)
from apps.workflows.services.submission_service import (
    submit_currency_purchase_create,
)

from apps.workflows.models import ApprovalRequest
from apps.workflows.services.approval_service import (
    approve_request,
    reject_request,
)
from unittest.mock import patch


User = get_user_model()


class ApprovalServiceTests(TestCase):
    def setUp(self):
        review_permission = Permission.objects.get(
            content_type__app_label="workflows",
            codename="review_approvalrequest",
        )

        self.supervisor_group = Group.objects.create(
            name="TRADE_SUPERVISOR",
        )
        self.supervisor_group.permissions.add(
            review_permission,
        )

        self.operator_group = Group.objects.create(
            name="TRADE_OPERATOR",
        )

        self.viewer_group = Group.objects.create(
            name="TRADE_VIEWER",
        )

        self.security_admin_group = Group.objects.create(
            name="SECURITY_ADMIN",
        )

        self.maker = User.objects.create_user(
            username="maker_user",
            password="test-password-123",
        )
        self.maker.groups.add(
            self.operator_group,
        )

        self.checker = User.objects.create_user(
            username="checker_user",
            password="test-password-123",
        )
        self.checker.groups.add(
            self.supervisor_group,
        )

        self.other_checker = User.objects.create_user(
            username="other_checker_user",
            password="test-password-123",
        )
        self.other_checker.groups.add(
            self.supervisor_group,
        )

        self.viewer = User.objects.create_user(
            username="viewer_user",
            password="test-password-123",
        )
        self.viewer.groups.add(
            self.viewer_group,
        )

        self.security_admin = User.objects.create_user(
            username="security_admin_user",
            password="test-password-123",
        )
        self.security_admin.groups.add(
            self.security_admin_group,
        )

        self.approval_request = ApprovalRequest.objects.create(
            operation=ApprovalRequest.Operation.CREATE,
            target_type="currency_purchase",
            reason="Maker correction reason.",
            payload={
                "amount": "1000.0000",
                "currency": "USD",
            },
            maker=self.maker,
        )

    def test_supervisor_can_approve_request(self):
        with patch(
                "apps.workflows.services.approval_service._apply_request"
        ) as mock_apply_request:
            mock_apply_request.return_value.pk = (
                self.approval_request.id
            )

            result = approve_request(
                approval_request=self.approval_request,
                checker=self.checker,
            )

        self.assertEqual(
            result.status,
            ApprovalRequest.Status.APPROVED,
        )
        self.assertEqual(
            result.checker,
            self.checker,
        )
        self.assertIsNotNone(
            result.reviewed_at,
        )

    def test_supervisor_can_reject_request_with_reason(self):
        result = reject_request(
            approval_request=self.approval_request,
            checker=self.checker,
            reason="Incorrect financial information.",
        )

        self.assertEqual(
            result.status,
            ApprovalRequest.Status.REJECTED,
        )
        self.assertEqual(
            result.checker,
            self.checker,
        )
        self.assertEqual(
            result.reason,
            "Maker correction reason.",
        )
        self.assertEqual(
            result.review_comment,
            "Incorrect financial information.",
        )
        self.assertIsNotNone(
            result.reviewed_at,
        )

    def test_maker_cannot_approve_own_request_even_with_permission(self):
        self.maker.groups.add(
            self.supervisor_group,
        )

        with self.assertRaises(ValidationError):
            approve_request(
                approval_request=self.approval_request,
                checker=self.maker,
            )

        self.approval_request.refresh_from_db()

        self.assertEqual(
            self.approval_request.status,
            ApprovalRequest.Status.PENDING,
        )
        self.assertIsNone(
            self.approval_request.checker,
        )
        self.assertIsNone(
            self.approval_request.reviewed_at,
        )

    def test_maker_cannot_reject_own_request_even_with_permission(self):
        self.maker.groups.add(
            self.supervisor_group,
        )

        with self.assertRaises(ValidationError):
            reject_request(
                approval_request=self.approval_request,
                checker=self.maker,
                reason="Self rejection attempt.",
            )

        self.approval_request.refresh_from_db()

        self.assertEqual(
            self.approval_request.status,
            ApprovalRequest.Status.PENDING,
        )
        self.assertIsNone(
            self.approval_request.checker,
        )
        self.assertIsNone(
            self.approval_request.reviewed_at,
        )

    def test_operator_cannot_approve_request(self):
        with self.assertRaises(ValidationError):
            approve_request(
                approval_request=self.approval_request,
                checker=self.maker,
            )

        self.approval_request.refresh_from_db()

        self.assertEqual(
            self.approval_request.status,
            ApprovalRequest.Status.PENDING,
        )

    def test_viewer_cannot_approve_request(self):
        with self.assertRaises(ValidationError):
            approve_request(
                approval_request=self.approval_request,
                checker=self.viewer,
            )

        self.approval_request.refresh_from_db()

        self.assertEqual(
            self.approval_request.status,
            ApprovalRequest.Status.PENDING,
        )

    def test_security_admin_cannot_approve_request(self):
        with self.assertRaises(ValidationError):
            approve_request(
                approval_request=self.approval_request,
                checker=self.security_admin,
            )

        self.approval_request.refresh_from_db()

        self.assertEqual(
            self.approval_request.status,
            ApprovalRequest.Status.PENDING,
        )

    def test_rejection_requires_reason(self):
        with self.assertRaises(ValidationError):
            reject_request(
                approval_request=self.approval_request,
                checker=self.checker,
                reason="   ",
            )

        self.approval_request.refresh_from_db()

        self.assertEqual(
            self.approval_request.status,
            ApprovalRequest.Status.PENDING,
        )
        self.assertIsNone(
            self.approval_request.checker,
        )
        self.assertIsNone(
            self.approval_request.reviewed_at,
        )

    def test_approved_request_cannot_be_reviewed_again(self):
        with patch(
                "apps.workflows.services.approval_service._apply_request"
        ) as mock_apply_request:
            mock_apply_request.return_value.pk = (
                self.approval_request.id
            )

            approve_request(
                approval_request=self.approval_request,
                checker=self.checker,
            )

        with self.assertRaises(ValidationError):
            reject_request(
                approval_request=self.approval_request,
                checker=self.other_checker,
                reason="Second review attempt.",
            )

        self.approval_request.refresh_from_db()

        self.assertEqual(
            self.approval_request.status,
            ApprovalRequest.Status.APPROVED,
        )
        self.assertEqual(
            self.approval_request.checker,
            self.checker,
        )

    def test_rejected_request_cannot_be_approved_again(self):
        reject_request(
            approval_request=self.approval_request,
            checker=self.checker,
            reason="Rejected by checker.",
        )

        with self.assertRaises(ValidationError):
            approve_request(
                approval_request=self.approval_request,
                checker=self.other_checker,
            )

        self.approval_request.refresh_from_db()

        self.assertEqual(
            self.approval_request.status,
            ApprovalRequest.Status.REJECTED,
        )
        self.assertEqual(
            self.approval_request.checker,
            self.checker,
        )

    def test_database_prevents_maker_being_checker(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ApprovalRequest.objects.filter(
                    pk=self.approval_request.pk,
                ).update(
                    status=ApprovalRequest.Status.APPROVED,
                    checker=self.maker,
                    reviewed_at=timezone.now(),
                )

        self.approval_request.refresh_from_db()

        self.assertEqual(
            self.approval_request.status,
            ApprovalRequest.Status.PENDING,
        )
        self.assertIsNone(
            self.approval_request.checker,
        )
        self.assertIsNone(
            self.approval_request.reviewed_at,
        )

    def test_database_prevents_approved_without_checker(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ApprovalRequest.objects.filter(
                    pk=self.approval_request.pk,
                ).update(
                    status=ApprovalRequest.Status.APPROVED,
                    checker=None,
                    reviewed_at=timezone.now(),
                )

        self.approval_request.refresh_from_db()

        self.assertEqual(
            self.approval_request.status,
            ApprovalRequest.Status.PENDING,
        )

    def test_database_prevents_approved_without_reviewed_at(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ApprovalRequest.objects.filter(
                    pk=self.approval_request.pk,
                ).update(
                    status=ApprovalRequest.Status.APPROVED,
                    checker=self.checker,
                    reviewed_at=None,
                )

        self.approval_request.refresh_from_db()

        self.assertEqual(
            self.approval_request.status,
            ApprovalRequest.Status.PENDING,
        )

    def test_database_prevents_pending_with_checker(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ApprovalRequest.objects.filter(
                    pk=self.approval_request.pk,
                ).update(
                    status=ApprovalRequest.Status.PENDING,
                    checker=self.checker,
                    reviewed_at=None,
                )

        self.approval_request.refresh_from_db()

        self.assertEqual(
            self.approval_request.status,
            ApprovalRequest.Status.PENDING,
        )
        self.assertIsNone(
            self.approval_request.checker,
        )

    def test_database_prevents_pending_with_reviewed_at(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ApprovalRequest.objects.filter(
                    pk=self.approval_request.pk,
                ).update(
                    status=ApprovalRequest.Status.PENDING,
                    checker=None,
                    reviewed_at=timezone.now(),
                )

        self.approval_request.refresh_from_db()

        self.assertEqual(
            self.approval_request.status,
            ApprovalRequest.Status.PENDING,
        )
        self.assertIsNone(
            self.approval_request.reviewed_at,
        )

from rest_framework import status
from rest_framework.test import APIClient


class ApprovalRequestAPITests(TestCase):
    def setUp(self):
        review_permission = Permission.objects.get(
            content_type__app_label="workflows",
            codename="review_approvalrequest",
        )

        add_purchase_permission = Permission.objects.get(
            content_type__app_label="trade_orders",
            codename="add_currencypurchase",
        )

        self.maker = User.objects.create_user(
            username="workflow-api-maker",
            password="StrongTestPassword123!",
        )
        self.maker.user_permissions.add(
            add_purchase_permission,
        )

        self.checker = User.objects.create_user(
            username="workflow-api-checker",
            password="StrongTestPassword123!",
        )
        self.checker.user_permissions.add(
            review_permission,
        )

        self.client = APIClient()

        self.company = Company.objects.create(
            name="Workflow API Company",
            national_id="WF-API-001",
            company_type=Company.CompanyType.COMMERCIAL,
        )

        self.order = RegistrationOrder.objects.create(
            company=self.company,
            order_number="WF-ORDER-001",
            registered_amount=Decimal("100000.0000"),
            currency="USD",
            is_active=True,
        )

    def test_supervisor_can_list_pending_approval_requests(self):
        ApprovalRequest.objects.create(
            operation=ApprovalRequest.Operation.CREATE,
            target_type="currency_purchase",
            payload={
                "registration_order_id": (
                    "00000000-0000-0000-0000-000000000001"
                ),
                "amount": "1000.0000",
                "currency": "USD",
                "purchase_date": "2026-09-11",
            },
            maker=self.maker,
        )

        self.client.force_authenticate(
            user=self.checker,
        )

        response = self.client.get(
            "/api/workflows/approval-requests/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["status"],
            ApprovalRequest.Status.PENDING,
        )

    def test_user_without_review_permission_cannot_list_requests(self):
        self.client.force_authenticate(
            user=self.maker,
        )

        response = self.client.get(
            "/api/workflows/approval-requests/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_checker_can_approve_request_through_api(self):
        approval_request = submit_currency_purchase_create(
            maker=self.maker,
            registration_order=self.order,
            amount=Decimal("25000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 11),
            reason="Purchase request.",
        )

        self.client.force_authenticate(
            user=self.checker,
        )

        response = self.client.post(
            (
                f"/api/workflows/approval-requests/"
                f"{approval_request.pk}/approve/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        approval_request.refresh_from_db()

        self.assertEqual(
            approval_request.status,
            ApprovalRequest.Status.APPROVED,
        )

        self.assertEqual(
            approval_request.checker,
            self.checker,
        )

        self.assertEqual(
            CurrencyPurchase.objects.count(),
            1,
        )

    def test_checker_can_reject_request_through_api(self):
        approval_request = submit_currency_purchase_create(
            maker=self.maker,
            registration_order=self.order,
            amount=Decimal("25000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 11),
            reason="Purchase request.",
        )

        self.client.force_authenticate(
            user=self.checker,
        )

        response = self.client.post(
            (
                f"/api/workflows/approval-requests/"
                f"{approval_request.pk}/reject/"
            ),
            {
                "reason": "Incorrect financial information.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        approval_request.refresh_from_db()

        self.assertEqual(
            approval_request.status,
            ApprovalRequest.Status.REJECTED,
        )

        self.assertEqual(
            approval_request.checker,
            self.checker,
        )

        self.assertEqual(
            approval_request.review_comment,
            "Incorrect financial information.",
        )

        self.assertEqual(
            CurrencyPurchase.objects.count(),
            0,
        )

    def test_reject_requires_reason_through_api(self):
        approval_request = submit_currency_purchase_create(
            maker=self.maker,
            registration_order=self.order,
            amount=Decimal("25000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 11),
        )

        self.client.force_authenticate(
            user=self.checker,
        )

        response = self.client.post(
            (
                f"/api/workflows/approval-requests/"
                f"{approval_request.pk}/reject/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        approval_request.refresh_from_db()

        self.assertEqual(
            approval_request.status,
            ApprovalRequest.Status.PENDING,
        )

    def test_maker_cannot_approve_own_request_through_api(self):
        review_permission = Permission.objects.get(
            content_type__app_label="workflows",
            codename="review_approvalrequest",
        )

        self.maker.user_permissions.add(
            review_permission,
        )

        approval_request = submit_currency_purchase_create(
            maker=self.maker,
            registration_order=self.order,
            amount=Decimal("25000.0000"),
            currency="USD",
            purchase_date=date(2026, 9, 11),
        )

        self.client.force_authenticate(
            user=self.maker,
        )

        response = self.client.post(
            (
                f"/api/workflows/approval-requests/"
                f"{approval_request.pk}/approve/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        approval_request.refresh_from_db()

        self.assertEqual(
            approval_request.status,
            ApprovalRequest.Status.PENDING,
        )

        self.assertIsNone(
            approval_request.checker,
        )

        self.assertEqual(
            CurrencyPurchase.objects.count(),
            0,
        )

    def test_direct_create_approval_request_is_not_allowed(self):
        self.client.force_authenticate(
            user=self.checker,
        )

        response = self.client.post(
            "/api/workflows/approval-requests/",
            {
                "operation": "CREATE",
                "target_type": "currency_purchase",
                "payload": {},
                "status": "APPROVED",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_direct_patch_approval_request_is_not_allowed(self):
        approval_request = ApprovalRequest.objects.create(
            operation=ApprovalRequest.Operation.CREATE,
            target_type="currency_purchase",
            payload={
                "registration_order_id": str(self.order.pk),
                "amount": "1000.0000",
                "currency": "USD",
                "purchase_date": "2026-09-11",
            },
            maker=self.maker,
        )

        self.client.force_authenticate(
            user=self.checker,
        )

        response = self.client.patch(
            (
                f"/api/workflows/approval-requests/"
                f"{approval_request.pk}/"
            ),
            {
                "status": "APPROVED",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_direct_put_approval_request_is_not_allowed(self):
        approval_request = ApprovalRequest.objects.create(
            operation=ApprovalRequest.Operation.CREATE,
            target_type="currency_purchase",
            payload={
                "registration_order_id": str(self.order.pk),
                "amount": "1000.0000",
                "currency": "USD",
                "purchase_date": "2026-09-11",
            },
            maker=self.maker,
        )

        self.client.force_authenticate(
            user=self.checker,
        )

        response = self.client.put(
            (
                f"/api/workflows/approval-requests/"
                f"{approval_request.pk}/"
            ),
            {
                "status": "APPROVED",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_direct_delete_approval_request_is_not_allowed(self):
        approval_request = ApprovalRequest.objects.create(
            operation=ApprovalRequest.Operation.CREATE,
            target_type="currency_purchase",
            payload={
                "registration_order_id": str(self.order.pk),
                "amount": "1000.0000",
                "currency": "USD",
                "purchase_date": "2026-09-11",
            },
            maker=self.maker,
        )

        self.client.force_authenticate(
            user=self.checker,
        )

        response = self.client.delete(
            (
                f"/api/workflows/approval-requests/"
                f"{approval_request.pk}/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )