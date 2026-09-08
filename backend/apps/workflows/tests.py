from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

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