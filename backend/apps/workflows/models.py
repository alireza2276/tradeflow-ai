import uuid

from django.conf import settings
from django.db import models


class ApprovalRequest(models.Model):
    class Operation(models.TextChoices):
        CREATE = "CREATE", "Create"
        CORRECT = "CORRECT", "Correct"
        VOID = "VOID", "Void"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    operation = models.CharField(
        max_length=20,
        choices=Operation.choices,
    )

    target_type = models.CharField(
        max_length=100,
    )

    target_id = models.UUIDField(
        null=True,
        blank=True,
    )

    payload = models.JSONField(
        default=dict,
    )

    reason = models.TextField(
        blank=True,
    )

    reason = models.TextField(
        blank=True,
    )

    review_comment = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    maker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="made_approval_requests",
    )

    checker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="checked_approval_requests",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "approval_requests"
        ordering = ["-created_at"]

        permissions = [
            (
                "review_approvalrequest",
                "Can approve or reject approval request",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=(
                        models.Q(checker__isnull=True)
                        | ~models.Q(maker=models.F("checker"))
                ),
                name="approval_checker_differs_from_maker",
            ),
            models.CheckConstraint(
                condition=(
                        models.Q(
                            status="PENDING",
                            checker__isnull=True,
                            reviewed_at__isnull=True,
                        )
                        | models.Q(
                    status__in=[
                        "APPROVED",
                        "REJECTED",
                    ],
                    checker__isnull=False,
                    reviewed_at__isnull=False,
                )
                ),
                name="approval_review_state_consistent",
            ),
        ]

        indexes = [
            models.Index(
                fields=["status", "created_at"],
                name="idx_approval_status_created",
            ),
            models.Index(
                fields=["target_type", "target_id"],
                name="idx_approval_target",
            ),
        ]

    def __str__(self):
        return (
            f"{self.operation} "
            f"{self.target_type} "
            f"- {self.status}"
        )