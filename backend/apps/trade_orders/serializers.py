from decimal import Decimal
from django.db.models import Sum

from rest_framework import serializers

from apps.common.services.date_service import format_dual_date

from apps.trade_orders.models import (
    CurrencyPurchase,
    PaymentInstrument,
    RegistrationOrder,
    ShipmentPart,
    RegulatoryRule,
    DeadlineExtension,
    CustomsClearance,
    RegulatoryDeadline,
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
            "activity_type",
            "shipment_deadline_months",
            "regulatory_rule_reference",
            "goods_category_code",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "company_name",
            "shipment_deadline_months",
            "regulatory_rule_reference",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        company = validated_data["company"]
        validated_data.setdefault(
            "activity_type",
            company.company_type,
        )
        return super().create(validated_data)

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

        activity_type = attrs.get(
            "activity_type",
            instance.activity_type,
        )
        deadline_months = attrs.get(
            "shipment_deadline_months",
            instance.shipment_deadline_months,
        )
        rule_reference = attrs.get(
            "regulatory_rule_reference",
            instance.regulatory_rule_reference,
        )
        goods_category_code = attrs.get(
            "goods_category_code",
            instance.goods_category_code,
        )

        if has_purchase_history and (
            activity_type != instance.activity_type
            or deadline_months != instance.shipment_deadline_months
            or rule_reference != instance.regulatory_rule_reference
            or goods_category_code != instance.goods_category_code
        ):
            raise serializers.ValidationError(
                {
                    "activity_type": (
                        "Regulatory classification cannot be changed after "
                        "currency-purchase history exists. Create a formal "
                        "correction/exception workflow instead."
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
            "operation_type",
            "issue_date",
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

    def validate(self, attrs):
        instance = self.instance
        if instance is not None and instance.registration_order.currency_purchases.exists():
            new_type = attrs.get("operation_type", instance.operation_type)
            new_date = attrs.get("issue_date", instance.issue_date)
            if new_type != instance.operation_type or new_date != instance.issue_date:
                raise serializers.ValidationError("Operation type/date cannot be changed after currency purchases exist. Use a controlled correction workflow.")
        return attrs

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
    regulatory_rule_reference = serializers.CharField(
        source="registration_order.regulatory_rule_reference",
        read_only=True,
    )
    shipment_deadline_months = serializers.IntegerField(
        source="registration_order.shipment_deadline_months",
        read_only=True,
    )
    activity_type = serializers.CharField(
        source="registration_order.activity_type",
        read_only=True,
    )

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
            "remittance_date",
            "funding_source_code",
            "original_deadline",
            "deadline",
            "deadline_dual",
            "deadline_extension_reference",
            "deadline_extension_reason",
            "regulatory_rule_reference",
            "shipment_deadline_months",
            "activity_type",
            "applied_rule",
            "obligation_status",
            "obligation_settled_at",
            "obligation_settled_by",
            "obligation_settlement_reason",
            "obligation_settlement_reference",
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
            "original_deadline",
            "deadline",
            "deadline_extension_reference",
            "deadline_extension_reason",
            "regulatory_rule_reference",
            "shipment_deadline_months",
            "activity_type",
            "applied_rule",
            "obligation_status",
            "obligation_settled_at",
            "obligation_settled_by",
            "obligation_settlement_reason",
            "obligation_settlement_reference",
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

class RegulatoryDeadlineSerializer(serializers.ModelSerializer):
    rule_code = serializers.CharField(source="applied_rule.code", read_only=True, allow_null=True)

    class Meta:
        model = RegulatoryDeadline
        fields = (
            "id", "currency_purchase", "deadline_kind", "rule_code",
            "basis_date", "original_deadline", "effective_deadline",
            "created_at", "updated_at",
        )
        read_only_fields = fields


class RegulatoryRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegulatoryRule
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class DeadlineExtensionSerializer(serializers.ModelSerializer):
    approved_by_name = serializers.CharField(source="approved_by.get_full_name", read_only=True)
    class Meta:
        model = DeadlineExtension
        fields = ("id", "currency_purchase", "regulatory_deadline", "previous_deadline", "new_deadline", "reason", "reference", "approved_by", "approved_by_name", "created_at")
        read_only_fields = ("id", "previous_deadline", "approved_by", "approved_by_name", "created_at")


class CustomsClearanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomsClearance
        fields = ("id", "currency_purchase", "declaration_number", "clearance_date", "amount", "status", "notes", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_amount(self, value):
        if value <= Decimal("0"):
            raise serializers.ValidationError("Clearance amount must be greater than zero.")
        return value
