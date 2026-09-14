import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class AuditEventQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError(
            "Audit events are immutable and cannot be updated."
        )

    def delete(self):
        raise ValidationError(
            "Audit events are immutable and cannot be deleted."
        )


class AuditEvent(models.Model):
    class Action(models.TextChoices):
        CREATE = "CREATE", "Create"
        UPDATE = "UPDATE", "Update"
        VOID = "VOID", "Void"
        DELETE = "DELETE", "Delete"
        REQUEST_SUBMITTED = (
            "REQUEST_SUBMITTED",
            "Request submitted",
        )
        REQUEST_APPROVED = (
            "REQUEST_APPROVED",
            "Request approved",
        )
        REQUEST_REJECTED = (
            "REQUEST_REJECTED",
            "Request rejected",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    action = models.CharField(
        max_length=40,
        choices=Action.choices,
        db_index=True,
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="audit_events",
        null=True,
        blank=True,
    )

    target_type = models.CharField(
        max_length=120,
        db_index=True,
    )

    target_id = models.CharField(
        max_length=120,
        blank=True,
        db_index=True,
    )

    approval_request = models.ForeignKey(
        "workflows.ApprovalRequest",
        on_delete=models.PROTECT,
        related_name="audit_events",
        null=True,
        blank=True,
    )

    before_state = models.JSONField(
        default=dict,
        blank=True,
    )

    after_state = models.JSONField(
        default=dict,
        blank=True,
    )

    reason = models.TextField(
        blank=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    objects = AuditEventQuerySet.as_manager()

    class Meta:
        db_table = "audit_events"
        ordering = ["-created_at"]
        permissions = [
            (
                "view_sensitive_audit",
                "Can view sensitive audit trail",
            ),
        ]
        indexes = [
            models.Index(
                fields=["target_type", "target_id", "created_at"],
                name="idx_audit_target_created",
            ),
            models.Index(
                fields=["actor", "created_at"],
                name="idx_audit_actor_created",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError(
                "Audit events are immutable and cannot be changed."
            )

        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError(
            "Audit events are immutable and cannot be deleted."
        )

    def __str__(self):
        return (
            f"{self.action} {self.target_type} "
            f"{self.target_id or '-'}"
        )
