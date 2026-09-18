from rest_framework import viewsets

from apps.authentication.permissions import (
    TradeFlowModelPermissions,
)
from apps.notifications.models import NotificationLog
from apps.notifications.serializers import NotificationLogSerializer


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (
        TradeFlowModelPermissions,
    )

    queryset = (
        NotificationLog.objects
        .select_related(
            "currency_purchase",
            "currency_purchase__registration_order",
            "currency_purchase__registration_order__company",
        )
        .all()
        .order_by("-created_at")
    )

    serializer_class = NotificationLogSerializer

    search_fields = (
        "notification_type",
        "currency_purchase__registration_order__order_number",
        "currency_purchase__registration_order__company__name",
        "currency_purchase__registration_order__company__national_id",
    )

    ordering_fields = (
        "created_at",
        "notification_type",
    )