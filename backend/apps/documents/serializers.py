from rest_framework import serializers

from apps.common.services.date_service import format_dual_date
from apps.documents.models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(
        source="shipment_part.currency_purchase.registration_order.order_number",
        read_only=True,
    )

    company_name = serializers.CharField(
        source="shipment_part.currency_purchase.registration_order.company.name",
        read_only=True,
    )

    order_currency = serializers.CharField(
        source="shipment_part.currency_purchase.registration_order.currency",
        read_only=True,
    )

    submission_date_dual = serializers.SerializerMethodField()

    class Meta:
        model = Invoice

        fields = (
            "id",
            "shipment_part",
            "order_number",
            "company_name",
            "order_currency",
            "fob_amount",
            "freight_amount",
            "total_amount",
            "submission_date",
            "submission_date_dual",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "order_number",
            "company_name",
            "order_currency",
            "total_amount",
            "submission_date_dual",
            "created_at",
            "updated_at",
        )

    def get_submission_date_dual(self, obj):
        return format_dual_date(
            obj.submission_date,
        )