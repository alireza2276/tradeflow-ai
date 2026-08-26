from rest_framework import serializers

from apps.common.services.date_service import format_dual_date
from apps.notifications.models import NotificationLog


class NotificationLogSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(
        source="currency_purchase.registration_order.company.name",
        read_only=True,
    )

    company_national_id = serializers.CharField(
        source="currency_purchase.registration_order.company.national_id",
        read_only=True,
    )

    order_number = serializers.CharField(
        source="currency_purchase.registration_order.order_number",
        read_only=True,
    )

    purchase_amount = serializers.DecimalField(
        source="currency_purchase.amount",
        max_digits=20,
        decimal_places=4,
        read_only=True,
    )

    currency = serializers.CharField(
        source="currency_purchase.currency",
        read_only=True,
    )

    purchase_date_dual = serializers.SerializerMethodField()
    deadline_dual = serializers.SerializerMethodField()

    class Meta:
        model = NotificationLog

        fields = (
            "id",
            "currency_purchase",
            "company_name",
            "company_national_id",
            "order_number",
            "purchase_amount",
            "currency",
            "purchase_date_dual",
            "deadline_dual",
            "notification_type",
            "sent_at",
        )

        read_only_fields = fields

    def get_purchase_date_dual(self, obj):
        return format_dual_date(
            obj.currency_purchase.purchase_date,
        )

    def get_deadline_dual(self, obj):
        return format_dual_date(
            obj.currency_purchase.deadline,
        )