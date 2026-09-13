from decimal import Decimal

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

    currency_purchase_amount = serializers.DecimalField(
        source="shipment_part.currency_purchase.amount",
        max_digits=20,
        decimal_places=4,
        read_only=True,
    )

    document_part_number = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    submission_date_dual = serializers.SerializerMethodField()

    class Meta:
        model = Invoice

        fields = (
            "id",
            "shipment_part",
            "order_number",
            "company_name",
            "order_currency",
            "currency_purchase_amount",
            "document_part_number",
            "fob_amount",
            "freight_amount",
            "total_amount",
            "remaining_amount",
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
            "currency_purchase_amount",
            "document_part_number",
            "total_amount",
            "remaining_amount",
            "submission_date_dual",
            "created_at",
            "updated_at",
        )

    def _get_purchase_invoice_summary(self, obj):
        """Return stable document-part and cumulative totals for one purchase.

        Invoices are numbered by the creation order of their linked shipment
        parts. The cache avoids one query per serializer field/row while still
        keeping these financial values server-authoritative.
        """
        purchase = obj.shipment_part.currency_purchase
        purchase_id = purchase.pk

        if not hasattr(self, "_purchase_summary_cache"):
            self._purchase_summary_cache = {}

        if purchase_id not in self._purchase_summary_cache:
            invoices = (
                Invoice.objects
                .filter(
                    shipment_part__currency_purchase_id=purchase_id,
                )
                .select_related("shipment_part")
                .order_by(
                    "shipment_part__created_at",
                    "created_at",
                    "id",
                )
            )

            cumulative_total = Decimal("0")
            invoice_summary = {}

            for part_number, invoice in enumerate(invoices, start=1):
                cumulative_total += invoice.total_amount
                invoice_summary[invoice.pk] = {
                    "document_part_number": part_number,
                    "remaining_amount": (
                        purchase.amount - cumulative_total
                    ),
                }

            self._purchase_summary_cache[purchase_id] = invoice_summary

        return self._purchase_summary_cache[purchase_id].get(
            obj.pk,
            {
                "document_part_number": 1,
                "remaining_amount": purchase.amount - obj.total_amount,
            },
        )

    def get_document_part_number(self, obj):
        summary = self._get_purchase_invoice_summary(obj)
        return summary["document_part_number"]

    def get_remaining_amount(self, obj):
        summary = self._get_purchase_invoice_summary(obj)
        return format(
            summary["remaining_amount"],
            "f",
        )

    def get_submission_date_dual(self, obj):
        return format_dual_date(
            obj.submission_date,
        )
