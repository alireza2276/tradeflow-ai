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

    purchase_date_dual = serializers.SerializerMethodField()
    deadline_dual = serializers.SerializerMethodField()

    class Meta:
        model = CurrencyPurchase

        fields = (
            "id",
            "registration_order",
            "order_number",
            "company_name",
            "amount",
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

    class Meta:
        model = ShipmentPart

        fields = (
            "id",
            "currency_purchase",
            "order_number",
            "company_name",
            "purchase_currency",
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
            "purchase_currency",
            "created_at",
            "updated_at",
        )