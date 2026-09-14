from rest_framework import serializers

from apps.audit.models import AuditEvent


class AuditEventSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(
        source="actor.username",
        read_only=True,
        allow_null=True,
    )

    approval_request_id = serializers.UUIDField(
        source="approval_request.id",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = AuditEvent
        fields = (
            "id",
            "action",
            "actor",
            "actor_username",
            "target_type",
            "target_id",
            "approval_request_id",
            "before_state",
            "after_state",
            "reason",
            "metadata",
            "created_at",
        )
        read_only_fields = fields
