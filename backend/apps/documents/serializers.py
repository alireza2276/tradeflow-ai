from decimal import Decimal

from rest_framework import serializers

from apps.common.services.date_service import format_dual_date
from apps.documents.models import Invoice
from apps.trade_orders.models import CurrencyPurchase


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

    registration_order_amount = serializers.SerializerMethodField()
    order_total_purchased = serializers.SerializerMethodField()
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
            "registration_order_amount",
            "order_total_purchased",
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
            "registration_order_amount",
            "order_total_purchased",
            "document_part_number",
            "total_amount",
            "remaining_amount",
            "submission_date_dual",
            "created_at",
            "updated_at",
        )

    def _get_order_invoice_summary(self, obj):
        """Return order-level document position for the current invoice.

        Currency purchases remain separate tranches so each keeps its own
        deadline. For display/reporting, however, document coverage is also
        shown at registration-order level. Therefore a later purchase for the
        same order immediately increases the remaining document amount while
        leaving every purchase deadline untouched.
        """
        order = obj.shipment_part.currency_purchase.registration_order
        order_id = order.pk

        if not hasattr(self, "_order_invoice_summary_cache"):
            self._order_invoice_summary_cache = {}

        if order_id not in self._order_invoice_summary_cache:
            # Keep aggregation explicit here so Decimal behaviour is stable
            # across supported database backends.
            active_purchases = CurrencyPurchase.objects.filter(
                registration_order_id=order_id,
                is_void=False,
            ).only("amount")
            total_purchased = sum(
                (purchase.amount for purchase in active_purchases),
                Decimal("0"),
            )

            invoices = (
                Invoice.objects
                .filter(
                    shipment_part__currency_purchase__registration_order_id=order_id,
                    shipment_part__currency_purchase__is_void=False,
                    shipment_part__is_void=False,
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
                    "remaining_amount": max(
                        total_purchased - cumulative_total,
                        Decimal("0"),
                    ),
                }

            self._order_invoice_summary_cache[order_id] = {
                "registration_order_amount": order.registered_amount,
                "total_purchased": total_purchased,
                "invoice_summary": invoice_summary,
            }

        return self._order_invoice_summary_cache[order_id]

    def _get_invoice_position(self, obj):
        summary = self._get_order_invoice_summary(obj)
        invoice_summary = summary["invoice_summary"]

        return invoice_summary.get(
            obj.pk,
            {
                "document_part_number": 1,
                "remaining_amount": max(
                    summary["total_purchased"] - obj.total_amount,
                    Decimal("0"),
                ),
            },
        )

    def get_registration_order_amount(self, obj):
        summary = self._get_order_invoice_summary(obj)
        return format(summary["registration_order_amount"], "f")

    def get_order_total_purchased(self, obj):
        summary = self._get_order_invoice_summary(obj)
        return format(summary["total_purchased"], "f")

    def get_document_part_number(self, obj):
        return self._get_invoice_position(obj)["document_part_number"]

    def get_remaining_amount(self, obj):
        return format(
            self._get_invoice_position(obj)["remaining_amount"],
            "f",
        )

    def get_submission_date_dual(self, obj):
        return format_dual_date(
            obj.submission_date,
        )
