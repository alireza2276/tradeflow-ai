from rest_framework import serializers

from apps.workflows.models import ApprovalRequest


class ApprovalRequestSerializer(
    serializers.ModelSerializer
):
    maker_username = serializers.CharField(
        source="maker.username",
        read_only=True,
    )

    checker_username = serializers.CharField(
        source="checker.username",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = ApprovalRequest

        fields = (
            "id",
            "operation",
            "target_type",
            "target_id",
            "payload",
            "reason",
            "status",
            "maker",
            "maker_username",
            "checker",
            "checker_username",
            "review_comment",
            "created_at",
            "reviewed_at",
        )

        read_only_fields = fields


class ApprovalRejectSerializer(
    serializers.Serializer
):
    reason = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )