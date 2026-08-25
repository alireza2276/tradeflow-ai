from decimal import Decimal

from rest_framework import serializers

from apps.trade_orders.models import RegistrationOrder

from apps.trade_orders.models import (
    PaymentInstrument,
    RegistrationOrder,
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