from decimal import Decimal

from rest_framework import serializers

from apps.common.services.date_service import format_dual_date
from apps.documents.models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(
        source=(
            "shipment_part.currency_purchase."
            "registration_order.order_number"
        ),
        read_only=True,
    )

    company_name = serializers.CharField(
        source=(
            "shipment_part.currency_purchase."
            "registration_order.company.name"
        ),
        read_only=True,
    )

    order_currency = serializers.CharField(
        source=(
            "shipment_part.currency_purchase."
            "registration_order.currency"
        ),
        read_only=True,
    )

    currency_purchase_amount = serializers.DecimalField(
        source="shipment_part.currency_purchase.amount",
        max_digits=20,
        decimal_places=4,
        read_only=True,
    )

    payment_instrument_number = serializers.CharField(
        source=(
            "shipment_part.currency_purchase."
            "registration_order.payment_instrument."
            "instrument_number"
        ),
        read_only=True,
        allow_null=True,
        default=None,
    )

    purchase_date = serializers.DateField(
        source="shipment_part.currency_purchase.purchase_date",
        read_only=True,
    )

    deadline = serializers.DateField(
        source="shipment_part.currency_purchase.deadline",
        read_only=True,
    )

    purchase_date_dual = serializers.SerializerMethodField()
    deadline_dual = serializers.SerializerMethodField()

    shipment_reference_number = serializers.CharField(
        source="shipment_part.reference_number",
        read_only=True,
    )

    shipment_amount = serializers.DecimalField(
        source="shipment_part.amount",
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
            "payment_instrument_number",
            "order_currency",
            "purchase_date",
            "purchase_date_dual",
            "deadline",
            "deadline_dual",
            "shipment_reference_number",
            "shipment_amount",
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
            "payment_instrument_number",
            "order_currency",
            "purchase_date",
            "purchase_date_dual",
            "deadline",
            "deadline_dual",
            "shipment_reference_number",
            "shipment_amount",
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

    def _get_purchase_invoice_summary(self, obj):
        """
        Return the invoice/document position for one currency purchase.

        Each CurrencyPurchase is treated as an independent tranche.
        Invoices related to one purchase reduce only that purchase's
        remaining document amount.

        A later currency purchase for the same registration order
        does not change the remaining amount of previous purchases.
        """
        purchase = obj.shipment_part.currency_purchase
        purchase_id = purchase.pk

        if not hasattr(
            self,
            "_purchase_invoice_summary_cache",
        ):
            self._purchase_invoice_summary_cache = {}

        if (
            purchase_id
            not in self._purchase_invoice_summary_cache
        ):
            invoices = (
                Invoice.objects
                .filter(
                    shipment_part__currency_purchase_id=(
                        purchase_id
                    ),
                    shipment_part__currency_purchase__is_void=False,
                    shipment_part__is_void=False,
                )
                .select_related(
                    "shipment_part",
                )
                .order_by(
                    "shipment_part__created_at",
                    "created_at",
                    "id",
                )
            )

            cumulative_total = Decimal("0")
            invoice_summary = {}

            for part_number, invoice in enumerate(
                invoices,
                start=1,
            ):
                cumulative_total += invoice.total_amount

                remaining_amount = max(
                    purchase.amount - cumulative_total,
                    Decimal("0"),
                )

                invoice_summary[invoice.pk] = {
                    "document_part_number": (
                        part_number
                    ),
                    "remaining_amount": (
                        remaining_amount
                    ),
                }

            self._purchase_invoice_summary_cache[
                purchase_id
            ] = {
                "purchase_amount": (
                    purchase.amount
                ),
                "invoice_summary": (
                    invoice_summary
                ),
            }

        return self._purchase_invoice_summary_cache[
            purchase_id
        ]

    def _get_invoice_position(self, obj):
        summary = (
            self._get_purchase_invoice_summary(
                obj
            )
        )

        invoice_summary = (
            summary["invoice_summary"]
        )

        return invoice_summary.get(
            obj.pk,
            {
                "document_part_number": 1,
                "remaining_amount": max(
                    summary["purchase_amount"]
                    - obj.total_amount,
                    Decimal("0"),
                ),
            },
        )

    def get_registration_order_amount(
        self,
        obj,
    ):
        order = (
            obj.shipment_part
            .currency_purchase
            .registration_order
        )

        return format(
            order.registered_amount,
            "f",
        )

    def get_order_total_purchased(
        self,
        obj,
    ):
        order = (
            obj.shipment_part
            .currency_purchase
            .registration_order
        )

        total_purchased = sum(
            (
                purchase.amount
                for purchase
                in order.currency_purchases.filter(
                    is_void=False,
                )
            ),
            Decimal("0"),
        )

        return format(
            total_purchased,
            "f",
        )

    def get_document_part_number(
        self,
        obj,
    ):
        return self._get_invoice_position(
            obj
        )["document_part_number"]

    def get_remaining_amount(
        self,
        obj,
    ):
        return format(
            self._get_invoice_position(
                obj
            )["remaining_amount"],
            "f",
        )

    def get_purchase_date_dual(
        self,
        obj,
    ):
        return format_dual_date(
            obj.shipment_part
            .currency_purchase
            .purchase_date
        )

    def get_deadline_dual(
        self,
        obj,
    ):
        return format_dual_date(
            obj.shipment_part
            .currency_purchase
            .deadline
        )

    def get_submission_date_dual(
        self,
        obj,
    ):
        return format_dual_date(
            obj.submission_date,
        )