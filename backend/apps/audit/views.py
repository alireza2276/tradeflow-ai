from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError

from apps.audit.models import AuditEvent
from apps.audit.serializers import AuditEventSerializer


class CanViewSensitiveAudit(permissions.BasePermission):
    message = "You do not have permission to view the audit trail."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.has_perm(
                "audit.view_sensitive_audit"
            )
        )


class AuditEventViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (CanViewSensitiveAudit,)
    serializer_class = AuditEventSerializer

    queryset = (
        AuditEvent.objects
        .select_related(
            "actor",
            "approval_request",
        )
        .all()
    )

    def get_queryset(self):
        queryset = super().get_queryset()

        action = self.request.query_params.get("action")
        target_type = self.request.query_params.get("target_type")
        actor = self.request.query_params.get("actor")

        if action:
            valid_actions = {
                choice[0]
                for choice in AuditEvent.Action.choices
            }

            if action not in valid_actions:
                raise ValidationError(
                    {"action": "Invalid audit action."}
                )

            queryset = queryset.filter(action=action)

        if target_type:
            queryset = queryset.filter(
                target_type=target_type
            )

        if actor:
            queryset = queryset.filter(actor_id=actor)

        return queryset
