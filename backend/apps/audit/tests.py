from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.audit.context import audit_context
from apps.audit.models import AuditEvent
from apps.companies.models import Company
from apps.workflows.models import ApprovalRequest


User = get_user_model()


class AuditTrailTests(TestCase):
    def setUp(self):
        self.maker = User.objects.create_user(
            username="audit-maker",
            password="test-pass-123",
        )
        self.checker = User.objects.create_user(
            username="audit-checker",
            password="test-pass-123",
        )

    def test_tracked_model_create_records_actor(self):
        with audit_context(
            actor=self.maker,
            metadata={"path": "/test/"},
        ):
            company = Company.objects.create(
                name="Audit Test Co",
                national_id="12345678901",
                company_type=Company.CompanyType.COMMERCIAL,
            )

        event = AuditEvent.objects.get(
            target_type="companies.company",
            target_id=str(company.pk),
            action=AuditEvent.Action.CREATE,
        )

        self.assertEqual(event.actor, self.maker)
        self.assertEqual(event.after_state["name"], "Audit Test Co")
        self.assertEqual(event.metadata["path"], "/test/")

    def test_approval_lifecycle_is_audited(self):
        request = ApprovalRequest.objects.create(
            operation=ApprovalRequest.Operation.CREATE,
            target_type="currency_purchase",
            payload={
                "registration_order_id": "00000000-0000-0000-0000-000000000001",
                "amount": "1000.0000",
                "currency": "EUR",
                "purchase_date": "2026-09-14",
            },
            reason="test submission",
            maker=self.maker,
        )

        submitted = AuditEvent.objects.get(
            approval_request=request,
            action=AuditEvent.Action.REQUEST_SUBMITTED,
        )
        self.assertEqual(submitted.actor, self.maker)

        request.status = ApprovalRequest.Status.REJECTED
        request.checker = self.checker
        request.review_comment = "test rejection"
        request.reviewed_at = timezone.now()
        request.save(
            update_fields=(
                "status",
                "checker",
                "review_comment",
                "reviewed_at",
            )
        )

        rejected = AuditEvent.objects.get(
            approval_request=request,
            action=AuditEvent.Action.REQUEST_REJECTED,
        )
        self.assertEqual(rejected.actor, self.checker)
        self.assertEqual(rejected.reason, "test rejection")

    def test_audit_event_is_immutable(self):
        event = AuditEvent.objects.create(
            action=AuditEvent.Action.CREATE,
            target_type="test.object",
            target_id="1",
        )

        event.reason = "changed"

        with self.assertRaises(ValidationError):
            event.save()

        with self.assertRaises(ValidationError):
            event.delete()
