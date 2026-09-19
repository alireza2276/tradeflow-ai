from rest_framework import serializers

from apps.common.services.date_service import format_dual_date
from apps.notifications.models import NotificationLog


class NotificationLogSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="currency_purchase.registration_order.company.name", read_only=True)
    company_national_id = serializers.CharField(source="currency_purchase.registration_order.company.national_id", read_only=True)
    order_number = serializers.CharField(source="currency_purchase.registration_order.order_number", read_only=True)
    purchase_amount = serializers.DecimalField(source="currency_purchase.amount", max_digits=20, decimal_places=4, read_only=True)
    currency = serializers.CharField(source="currency_purchase.currency", read_only=True)
    purchase_date_dual = serializers.SerializerMethodField()
    deadline_dual = serializers.SerializerMethodField()
    sent_at = serializers.DateTimeField(source="created_at", read_only=True)
    sms_sent_count = serializers.SerializerMethodField()
    sms_failed_count = serializers.SerializerMethodField()

    class Meta:
        model = NotificationLog
        fields = (
            "id", "currency_purchase", "company_name", "company_national_id", "order_number",
            "purchase_amount", "currency", "purchase_date_dual", "deadline_dual",
            "deadline_kind", "notification_type", "message", "sms_sent_count", "sms_failed_count", "sent_at",
        )
        read_only_fields = fields

    def get_purchase_date_dual(self, obj):
        return format_dual_date(obj.currency_purchase.purchase_date)

    def get_deadline_dual(self, obj):
        return format_dual_date(obj.deadline_date or obj.currency_purchase.deadline)

    def get_sms_sent_count(self, obj):
        annotated = getattr(obj, "sms_sent_count_db", None)
        if annotated is not None:
            return annotated
        return obj.deliveries.filter(channel="SMS", status="SENT").count()

    def get_sms_failed_count(self, obj):
        annotated = getattr(obj, "sms_failed_count_db", None)
        if annotated is not None:
            return annotated
        return obj.deliveries.filter(channel="SMS", status__in=["FAILED", "SKIPPED"]).count()
