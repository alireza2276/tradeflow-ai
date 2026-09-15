from decimal import Decimal
from django.db.models import Sum

from rest_framework import serializers

from apps.common.services.date_service import format_dual_date

from apps.trade_orders.models import (
    CurrencyPurchase,
    PaymentInstrument,
    RegistrationOrder,
    ShipmentPart,
)

class RegistrationOrderSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(
        source="company.name",
        read_only=True,
    )

    class Meta:
        model = RegistrationOrder

        fields = (
            "id",
            "company",
            "company_name",
            "order_number",
            "registered_amount",
            "currency",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "company_name",
            "created_at",
            "updated_at",
        )

    def validate_registered_amount(self, value):
        if value <= Decimal("0"):
            raise serializers.ValidationError(
                "Registered amount must be greater than zero."
            )

        return value

    def validate_currency(self, value):
        value = value.strip().upper()

        if len(value) != 3 or not value.isalpha():
            raise serializers.ValidationError(
                "Currency must be a valid 3-letter code."
            )

        return value

    def validate(self, attrs):
        instance = self.instance

        if instance is None:
            return attrs

        registered_amount = attrs.get(
            "registered_amount",
            instance.registered_amount,
        )

        currency = attrs.get(
            "currency",
            instance.currency,
        )

        active_total_purchased = (
            instance.currency_purchases.filter(
                is_void=False,
            ).aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0")
        )

        has_purchase_history = (
            instance.currency_purchases.exists()
        )

        if registered_amount < active_total_purchased:
            raise serializers.ValidationError(
                {
                    "registered_amount": (
                        "Registered amount cannot be lower "
                        "than the total currency purchases."
                    )
                }
            )

        if (
            has_purchase_history
            and currency != instance.currency
        ):
            raise serializers.ValidationError(
                {
                    "currency": (
                        "Currency cannot be changed because "
                        "currency purchases already exist "
                        "for this registration order."
                    )
                }
            )

        return attrs


class PaymentInstrumentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(
        source="registration_order.order_number",
        read_only=True,
    )

    company_name = serializers.CharField(
        source="registration_order.company.name",
        read_only=True,
    )

    class Meta:
        model = PaymentInstrument

        fields = (
            "id",
            "registration_order",
            "order_number",
            "company_name",
            "instrument_number",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "order_number",
            "company_name",
            "created_at",
            "updated_at",
        )

class CurrencyPurchaseSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(
        source="registration_order.order_number",
        read_only=True,
    )

    company_name = serializers.CharField(
        source="registration_order.company.name",
        read_only=True,
    )
    payment_instrument_number = serializers.CharField(
        source="registration_order.payment_instrument.instrument_number",
        read_only=True,
        allow_null=True,
        default=None,
    )


    purchase_date_dual = serializers.SerializerMethodField()
    deadline_dual = serializers.SerializerMethodField()
    purchase_sequence = serializers.SerializerMethodField()
    registration_order_amount = serializers.SerializerMethodField()
    order_total_purchased = serializers.SerializerMethodField()
    order_remaining_to_purchase = serializers.SerializerMethodField()

    class Meta:
        model = CurrencyPurchase

        fields = (
            "id",
            "registration_order",
            "order_number",
            "company_name",
            "payment_instrument_number",
            "purchase_sequence",
            "amount",
            "registration_order_amount",
            "order_total_purchased",
            "order_remaining_to_purchase",
            "currency",
            "purchase_date",
            "purchase_date_dual",
            "deadline",
            "deadline_dual",
            "is_void",
            "voided_at",
            "voided_by",
            "void_reason",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "order_number",
            "company_name",
            "purchase_sequence",
            "registration_order_amount",
            "order_total_purchased",
            "order_remaining_to_purchase",
            "deadline",
            "purchase_date_dual",
            "deadline_dual",
            "is_void",
            "voided_at",
            "voided_by",
            "void_reason",
            "created_at",
            "updated_at",
        )

    def _get_order_purchase_summary(self, obj):
        """Return active purchase totals without merging purchase records.

        Each CurrencyPurchase remains an independent tranche with its own
        purchase date and deadline. Only the display totals are aggregated at
        registration-order level.
        """
        order = obj.registration_order
        order_id = order.pk

        if not hasattr(self, "_order_purchase_summary_cache"):
            self._order_purchase_summary_cache = {}

        if order_id not in self._order_purchase_summary_cache:
            purchases = list(
                order.currency_purchases
                .filter(is_void=False)
                .order_by("purchase_date", "created_at", "id")
            )

            running_total = Decimal("0")
            position_by_id = {}

            for index, purchase in enumerate(purchases, start=1):
                running_total += purchase.amount
                position_by_id[purchase.pk] = {
                    "sequence": index,
                    "total_purchased": running_total,
                    "remaining_to_purchase": max(
                        order.registered_amount - running_total,
                        Decimal("0"),
                    ),
                }

            self._order_purchase_summary_cache[order_id] = {
                "position_by_id": position_by_id,
            }

        return self._order_purchase_summary_cache[order_id]

    def get_purchase_sequence(self, obj):
        if obj.is_void:
            return None

        summary = self._get_order_purchase_summary(obj)
        position = summary["position_by_id"].get(obj.pk)
        return position["sequence"] if position else None

    def get_registration_order_amount(self, obj):
        return format(obj.registration_order.registered_amount, "f")

    def get_order_total_purchased(self, obj):
        summary = self._get_order_purchase_summary(obj)
        position = summary["position_by_id"].get(obj.pk)

        if position is None:
            return format(Decimal("0"), "f")

        return format(position["total_purchased"], "f")

    def get_order_remaining_to_purchase(self, obj):
        summary = self._get_order_purchase_summary(obj)
        position = summary["position_by_id"].get(obj.pk)

        if position is None:
            return format(obj.registration_order.registered_amount, "f")

        return format(position["remaining_to_purchase"], "f")

    def get_purchase_date_dual(self, obj):
        return format_dual_date(
            obj.purchase_date,
        )

    def get_deadline_dual(self, obj):
        return format_dual_date(
            obj.deadline,
        )


class ShipmentPartSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(
        source="currency_purchase.registration_order.order_number",
        read_only=True,
    )

    company_name = serializers.CharField(
        source="currency_purchase.registration_order.company.name",
        read_only=True,
    )

    purchase_currency = serializers.CharField(
        source="currency_purchase.currency",
        read_only=True,
    )

    currency_purchase_amount = serializers.DecimalField(
        source="currency_purchase.amount",
        max_digits=20,
        decimal_places=4,
        read_only=True,
    )

    payment_instrument_number = serializers.CharField(
        source=(
            "currency_purchase.registration_order."
            "payment_instrument.instrument_number"
        ),
        read_only=True,
        allow_null=True,
        default=None,
    )

    purchase_date = serializers.DateField(
        source="currency_purchase.purchase_date",
        read_only=True,
    )

    purchase_date_dual = serializers.SerializerMethodField()

    deadline = serializers.DateField(
        source="currency_purchase.deadline",
        read_only=True,
    )

    deadline_dual = serializers.SerializerMethodField()


    class Meta:
        model = ShipmentPart

        fields = (
            "id",
            "currency_purchase",
            "order_number",
            "company_name",
            "payment_instrument_number",
            "purchase_currency",
            "currency_purchase_amount",
            "purchase_date",
            "purchase_date_dual",
            "deadline",
            "deadline_dual",
            "amount",
            "shipment_date",
            "received_date",
            "reference_number",
            "notes",
            "is_void",
            "voided_at",
            "voided_by",
            "void_reason",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "order_number",
            "company_name",
            "payment_instrument_number",
            "purchase_currency",
            "currency_purchase_amount",
            "purchase_date",
            "purchase_date_dual",
            "deadline",
            "deadline_dual",
            "created_at",
            "updated_at",
        )


    def get_purchase_date_dual(self, obj):
        return format_dual_date(
            obj.currency_purchase.purchase_date,
        )


    def get_deadline_dual(self, obj):
        return format_dual_date(
            obj.currency_purchase.deadline,
        )
