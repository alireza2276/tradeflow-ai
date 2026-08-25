from django.contrib import admin

from apps.common.services.date_service import format_dual_date
from apps.trade_orders.models import (
    CurrencyPurchase,
    PaymentInstrument,
    RegistrationOrder,
    ShipmentPart,
)
from apps.trade_orders.services.balance_service import (
    get_purchase_balance,
)


@admin.register(RegistrationOrder)
class RegistrationOrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "company",
        "registered_amount",
        "currency",
        "is_active",
        "created_at",
    )

    search_fields = (
        "order_number",
        "company__name",
        "company__national_id",
    )

    list_filter = (
        "currency",
        "is_active",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )


@admin.register(PaymentInstrument)
class PaymentInstrumentAdmin(admin.ModelAdmin):
    list_display = (
        "instrument_number",
        "registration_order",
        "created_at",
    )

    search_fields = (
        "instrument_number",
        "registration_order__order_number",
        "registration_order__company__name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )


@admin.register(CurrencyPurchase)
class CurrencyPurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "registration_order",
        "amount",
        "currency",
        "purchase_date_dual",
        "deadline_dual",
        "documented_amount_display",
        "remaining_amount_display",
    )

    search_fields = (
        "registration_order__order_number",
        "registration_order__company__name",
        "registration_order__company__national_id",
    )

    list_filter = (
        "currency",
        "registration_order__company__company_type",
    )

    readonly_fields = (
        "id",
        "deadline",
        "purchase_date_dual",
        "deadline_dual",
        "documented_amount_display",
        "remaining_amount_display",
        "created_at",
        "updated_at",
    )

    def purchase_date_dual(self, obj):
        return format_dual_date(obj.purchase_date)

    purchase_date_dual.short_description = "Purchase Date"

    def deadline_dual(self, obj):
        return format_dual_date(obj.deadline)

    deadline_dual.short_description = "Deadline"

    def documented_amount_display(self, obj):
        balance = get_purchase_balance(
            purchase=obj,
        )
        return f"{balance['documented_amount']} {obj.currency}"

    documented_amount_display.short_description = "Documented"

    def remaining_amount_display(self, obj):
        balance = get_purchase_balance(
            purchase=obj,
        )
        return f"{balance['remaining_amount']} {obj.currency}"

    remaining_amount_display.short_description = "Remaining"


@admin.register(ShipmentPart)
class ShipmentPartAdmin(admin.ModelAdmin):
    list_display = (
        "currency_purchase",
        "amount",
        "shipment_date",
        "received_date",
        "reference_number",
        "created_at",
    )

    search_fields = (
        "reference_number",
        "currency_purchase__registration_order__order_number",
        "currency_purchase__registration_order__company__name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )